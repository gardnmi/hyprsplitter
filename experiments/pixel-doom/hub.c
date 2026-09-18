/* Shared terminal renderer. Helpers transfer their PTY and exit; Foot -H
 * keeps the real terminal window alive while this process owns the slave FD. */
#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/mman.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <time.h>
#include <stdatomic.h>

static uint64_t millis(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);
    return (uint64_t)t.tv_sec*1000+t.tv_nsec/1000000;
}
static struct sockaddr_un address(const char *path) {
    struct sockaddr_un a={.sun_family=AF_UNIX};
    if(strlen(path)>=sizeof(a.sun_path)) { fprintf(stderr,"Socket path too long\n"); exit(1); }
    strcpy(a.sun_path,path); return a;
}
static int attach(const char *path,int index) {
    struct termios t;
    if(tcgetattr(0,&t)) return 1;
    cfmakeraw(&t); tcsetattr(0,TCSANOW,&t);
    /* The shared renderer will handle both subsequent output and keyboard input. */
    const char init[]="\033[?25l\033[2J";
    if(write(1,init,sizeof(init)-1)!=(ssize_t)sizeof(init)-1) return 1;
    int s=socket(AF_UNIX,SOCK_DGRAM,0);
    struct sockaddr_un a=address(path);
    char ancillary[CMSG_SPACE(sizeof(int))]={0};
    struct iovec iov={.iov_base=&index,.iov_len=sizeof(index)};
    struct msghdr msg={.msg_name=&a,.msg_namelen=sizeof(a),.msg_iov=&iov,
        .msg_iovlen=1,.msg_control=ancillary,.msg_controllen=sizeof(ancillary)};
    struct cmsghdr *c=CMSG_FIRSTHDR(&msg);
    c->cmsg_level=SOL_SOCKET; c->cmsg_type=SCM_RIGHTS; c->cmsg_len=CMSG_LEN(sizeof(int));
    int fd=1; memcpy(CMSG_DATA(c),&fd,sizeof(fd));
    int ok=sendmsg(s,&msg,0)==sizeof(index); close(s);
    return ok?0:1;
}
struct pixel { int fd,index,color,next,len,sent; char output[32]; };
static void flush(struct pixel *p) {
    while(p->sent<p->len) {
        ssize_t n=write(p->fd,p->output+p->sent,p->len-p->sent);
        if(n<0 && errno==EINTR) continue;
        if(n<0 && (errno==EAGAIN || errno==EWOULDBLOCK)) return;
        if(n<=0) { close(p->fd); p->fd=-1; return; }
        p->sent+=n;
    }
    if(p->len) p->color=p->next;
    p->len=p->sent=0;
}
/* Optional progressive layout: sequence protects geometry while a tile splits. */
struct region { _Atomic uint32_t sequence; uint16_t x0,y0,x1,y1; uint32_t reserved; };
_Static_assert(sizeof(struct region)==16,"region layout");
static int region_color(const unsigned char *rgb,const struct region *r,int *color) {
    uint32_t before=atomic_load_explicit(&r->sequence,memory_order_acquire);
    if(before&1) return 0;
    uint16_t x0=r->x0,y0=r->y0,x1=r->x1,y1=r->y1;
    atomic_thread_fence(memory_order_acquire);
    if(before!=atomic_load_explicit(&r->sequence,memory_order_acquire) ||
       x1<=x0 || y1<=y0 || x1>320 || y1>200) return 0;
    unsigned red=0,green=0,blue=0,n=(x1-x0)*(y1-y0);
    for(unsigned y=y0;y<y1;y++) for(unsigned x=x0;x<x1;x++) {
        const unsigned char *p=rgb+(y*320+x)*3;
        red+=p[0];green+=p[1];blue+=p[2];
    }
    *color=((red/n)<<16)|((green/n)<<8)|(blue/n);return 1;
}
int main(int argc,char **argv) {
    if(argc==4 && !strcmp(argv[1],"attach")) return attach(argv[2],atoi(argv[3]));
    if(argc!=6 && argc!=7) { fprintf(stderr,"hub FRAME SOCKET KEYS CAPACITY FPS [REGIONS]\n"); return 1; }
    int capacity=atoi(argv[4]),fps=atoi(argv[5]);
    if(capacity<1 || capacity>2048 || fps<1 || fps>35) return 1;
    int f=open(argv[1],O_RDONLY); struct stat st;
    if(f<0 || fstat(f,&st) || st.st_size<3) return 1;
    unsigned char *rgb=mmap(NULL,st.st_size,PROT_READ,MAP_SHARED,f,0); close(f);
    if(rgb==MAP_FAILED) return 1;
    struct region *regions=NULL;size_t region_count=0;
    if(argc==7) {
        int rf=open(argv[6],O_RDONLY);struct stat rs;
        if(st.st_size!=320*200*3 || rf<0 || fstat(rf,&rs) || rs.st_size<16 || rs.st_size%16) return 1;
        regions=mmap(NULL,rs.st_size,PROT_READ,MAP_SHARED,rf,0);close(rf);
        if(regions==MAP_FAILED) return 1;
        region_count=rs.st_size/16;
    }
    int s=socket(AF_UNIX,SOCK_DGRAM|SOCK_NONBLOCK,0), ep=epoll_create1(EPOLL_CLOEXEC);
    struct sockaddr_un a=address(argv[2]),keyaddr=address(argv[3]);
    if(s<0 || ep<0 || bind(s,(void*)&a,sizeof(a))) { perror("hub socket"); return 1; }
    struct epoll_event ev={.events=EPOLLIN,.data.fd=s}; epoll_ctl(ep,EPOLL_CTL_ADD,s,&ev);
    struct pixel *pixels=calloc(capacity,sizeof(*pixels)); int count=0;
    uint64_t next_frame=0; signal(SIGPIPE,SIG_IGN);
    for(;;) {
        uint64_t now=millis(); int delay=next_frame>now?(int)(next_frame-now):0;
        struct epoll_event events[64]; int n=epoll_wait(ep,events,64,delay);
        for(int j=0;j<n;j++) {
            int fd=events[j].data.fd;
            if(fd==s) {
                int index=-2;
                char ancillary[CMSG_SPACE(sizeof(int))]={0};
                struct iovec iov={.iov_base=&index,.iov_len=sizeof(index)};
                struct msghdr msg={.msg_iov=&iov,.msg_iovlen=1,
                    .msg_control=ancillary,.msg_controllen=sizeof(ancillary)};
                ssize_t got=recvmsg(s,&msg,MSG_CMSG_CLOEXEC);
                struct cmsghdr *c=CMSG_FIRSTHDR(&msg); int tty=-1;
                if(c && c->cmsg_level==SOL_SOCKET && c->cmsg_type==SCM_RIGHTS &&
                   c->cmsg_len==CMSG_LEN(sizeof(int))) memcpy(&tty,CMSG_DATA(c),sizeof(tty));
                if(tty<0) continue;
                if(got!=sizeof(index) || (msg.msg_flags&(MSG_TRUNC|MSG_CTRUNC)) ||
                   count>=capacity || index < -1 || (index>=0 && (regions ? (size_t)index>=region_count : (off_t)index*3+2>=st.st_size))) {
                    close(tty); continue;
                }
                fcntl(tty,F_SETFL,fcntl(tty,F_GETFL)|O_NONBLOCK);
                pixels[count++]=(struct pixel){.fd=tty,.index=index,.color=-1};
                ev=(struct epoll_event){.events=EPOLLIN,.data.fd=tty};
                epoll_ctl(ep,EPOLL_CTL_ADD,tty,&ev);
            } else {
                char input[128]; ssize_t got=read(fd,input,sizeof(input));
                if(got>0) sendto(s,input,got,MSG_DONTWAIT,(void*)&keyaddr,sizeof(keyaddr));
                if((events[j].events&(EPOLLHUP|EPOLLERR)) || got==0) {
                    epoll_ctl(ep,EPOLL_CTL_DEL,fd,NULL);
                    for(int k=0;k<count;k++) if(pixels[k].fd==fd) pixels[k].fd=-1;
                    close(fd);
                }
            }
        }
        now=millis(); if(now<next_frame) continue;
        next_frame=now+1000/fps;
        for(int j=0;j<count;j++) {
            struct pixel *p=&pixels[j]; if(p->fd<0) continue;
            flush(p); if(p->fd<0 || p->len) continue;
            int i=p->index*3;
            int color=p->index<0?0:((int)rgb[i]<<16)|((int)rgb[i+1]<<8)|rgb[i+2];
            if(regions && p->index>=0 && !region_color(rgb,&regions[p->index],&color)) continue;
            if(color==p->color) continue;
            p->next=color; p->len=snprintf(p->output,sizeof(p->output),"\033]11;#%06x\a",color);
            flush(p);
        }
    }
}
