# Quantum-tic-tac-toe
## Potreban software
Za pokretanje programa potrebni su paketi: networkx, deepcopy i unittest.
```bash
pip install networkx
```
## Testiranje koda
Testni primjeri se pišu u test.py.
```python
from Game import *
def test(self):
    new_game = Game('cpu', 'cpu') # cpu == minimax bot, bilošto drugo == player
    new_game.make_move((Mark('x', 1), 2, 3), []) # potezi su oblika (oznaka, pozicija1, pozicija2) u slučaju u kojem nepostoje raspadna stanja
                                                 # make_move se poziva ovako: make_move(potez, []), prazna lista na kraju funkcije je nužna
                                                 # u slučaju raspadnog stanja make_move prima potez oblika (oznaka, pozicija), pozicija2 nije potrebna
    score = new_game.run_minimax() # igra vraća konačan broj bodova igrača x, x je prvi igrač
    self.assertTrue(score == 1)
```