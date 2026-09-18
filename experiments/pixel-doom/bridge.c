/* Local DOOM experiment: one downsampled pixel per actual foot terminal. */
#define _DEFAULT_SOURCE
#include "doomgeneric.h"
#include "doomstat.h"
extern int demosequence;
extern char *defdemoname;
extern boolean singletics;
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <time.h>

static unsigned char *frame;
static int cols, rows;
static unsigned output_interval_ms = 65;
uint32_t DG_GetTicksMs(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint32_t)(t.tv_sec * 1000 + t.tv_nsec / 1000000);
}
void DG_Init(void) {}
void DG_SleepMs(uint32_t ms) { usleep(ms * 1000); }
void DG_SetWindowTitle(const char *title) { (void)title; }
int DG_GetKey(int *pressed, unsigned char *key) {
    unsigned char pair[2];
    if (read(0, pair, 2) != 2) return 0;
    *pressed = pair[0]; *key = pair[1]; return 1;
}
void DG_DrawFrame(void) {
    static uint32_t last;
    uint32_t now = DG_GetTicksMs();
    if (now - last < output_interval_ms) return;
    last = now;
    for (int y = 0; y < rows; y++) for (int x = 0; x < cols; x++) {
        unsigned r=0, g=0, b=0, n=0;
        for (int sy=y*200/rows; sy<(y+1)*200/rows; sy++)
            for (int sx=x*320/cols; sx<(x+1)*320/cols; sx++) {
                uint32_t p=DG_ScreenBuffer[sy*320+sx];
                r+=(p>>16)&255; g+=(p>>8)&255; b+=p&255; n++;
            }
        int i=(y*cols+x)*3;
        frame[i]=r/n; frame[i+1]=g/n; frame[i+2]=b/n;
    }
}
static int pixel(const char *path, int index, const char *socketpath, int fps) {
    if(fps<1 || fps>35) return 1;
    int fd=open(path,O_RDONLY);
    if(fd<0) return 1;
    off_t size=lseek(fd,0,SEEK_END);
    unsigned char *data=mmap(NULL,size,PROT_READ,MAP_SHARED,fd,0);
    if(data==MAP_FAILED || index<0 || index*3+2>=size) return 1;
    close(fd);
    int sock=socket(AF_UNIX,SOCK_DGRAM,0);
    struct sockaddr_un addr={.sun_family=AF_UNIX};
    snprintf(addr.sun_path,sizeof(addr.sun_path),"%s",socketpath);
    struct termios t;
    tcgetattr(0,&t); cfmakeraw(&t); tcsetattr(0,TCSANOW,&t);
    fcntl(0,F_SETFL,O_NONBLOCK);
    printf("\033[?25l\033[2J"); fflush(stdout);
    int old=-1;
    for (;;) {
        int i=index*3, r=data[i], g=data[i+1], b=data[i+2];
        int color=(r<<16)|(g<<8)|b;
        if(color!=old) {
            /* OSC 11 already damages default-color cells and margins in foot.
             * Clearing the screen again doubles work for this empty terminal. */
            printf("\033]11;#%06x\a",color);
            fflush(stdout); old=color;
        }
        char input[128]; int n=read(0,input,sizeof(input));
        if(n>0) sendto(sock,input,n,0,(void*)&addr,sizeof(addr));
        usleep(1000000/fps);
    }
}
int main(int argc,char **argv) {
    if(argc>=5 && !strcmp(argv[1],"pixel")) return pixel(argv[2],atoi(argv[3]),argv[4],argc>5?atoi(argv[5]):15);
    if(argc<6) return 1;
    const char *requested_fps=getenv("PIXEL_DOOM_OUTPUT_FPS");
    if(requested_fps) {
        int fps=atoi(requested_fps);
        if(fps<1 || fps>35) { fprintf(stderr,"Output FPS must be 1–35\n"); return 1; }
        /* Preserve prior production cadence for low-FPS renderer comparisons. */
        if(fps>15) output_interval_ms=1000/fps;
    }
    cols=atoi(argv[2]); rows=atoi(argv[3]);
    int fd=open(argv[1],O_RDWR);
    frame=mmap(NULL,cols*rows*3,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
    if(frame==MAP_FAILED) return 1;
    close(fd); fcntl(0,F_SETFL,O_NONBLOCK);
    doomgeneric_Create(argc-3,argv+3);
    const int loop_demo=getenv("PIXEL_DOOM_LOOP_DEMO")!=NULL;
    if(loop_demo) {
        // D_DoomMain returns in doomgeneric; its local demolumpname no longer
        // exists. Keep the name valid when G_CheckDemoStatus releases the lump.
        static char stable_demo_name[]="demo1";
        defdemoname=stable_demo_name;
        singledemo=false;
    }
#ifdef PIXEL_DOOM_TEST_FAST
    singletics=true;
    unsigned test_ticks=0;
#endif
    for(;;) {
        // Native attract-mode advancement selects demo1 directly, omitting title
        // cards. The same engine stays alive after the recorded demo ends.
        if(loop_demo) demosequence=0;
        doomgeneric_Tick();
#ifdef PIXEL_DOOM_TEST_FAST
        if(++test_ticks==18000) {
            fprintf(stderr,"LOOP_TEST_PASSED: 18000 game ticks in one process\n");
            return 0;
        }
#endif
    }
}
