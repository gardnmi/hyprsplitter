# Two-window docking game

Drag the small window completely inside the large dock. The windows turn green
when you succeed. **R** resets; **Escape** or closing either window exits.

Run `python main.py` from this directory, or launch its generated cartridge.
Requires the Omarchy/GTK3 dependencies from the root README.

- `model.py`: pure containment rule.
- `main.py`: scoped native windows, input, animation, cleanup.
- `test_model.py`: behavior tests.

Start extending this by changing the objective in the model, then the visuals.
See the repository's `docs/ADDING_A_GAME.md` for the integration contract.
