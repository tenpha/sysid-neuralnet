import numpy as np
import numpy.random as rd
from torch.utils.data import Dataset


class ChenDataset(Dataset):
    """Implement data generator for nonlinear example in _[1].

    Parameters
    ----------
    seq_len: int
        Sequence lenght for a batch on the dataset.
    ntotbatch: int
        Total number of batches.
    burnout: int
        Number of sequences to be discarded (removing the transient behaviour).
    seed: int
        Random seed.
    sd_v, sd_w: float
        Standard deviation for process and output noise (respectively)

    References
    ----------
     .. [1] S. Chen, S. A. Billings, P. M. Grant, Non-Linear System Identification Using
            Neural Networks, International Journal of Control 51 (6) (1990) 1191–1214.
    """
    def __init__(self, seq_len, ntotbatch, burnout=100, seed=1, sd_v=0.1, sd_w=0.5):
        self.seed = seed
        self.rng = rd.RandomState(seed)
        self.seq_len = seq_len
        self.ntotbatch = ntotbatch
        self.burnout = burnout
        self.sd_v, self.sd_w = sd_v, sd_w
        self.u, self.y = self._gen_data()
        self.sd_v, self.sd_w = sd_v, sd_w
        self.nu = 1
        self.ny = 1

    def _gen_data(self):
        total_lenght = self.seq_len*self.ntotbatch + self.burnout

        u = self._generate_random_input(total_lenght, 5)
        y = self._simulate_system(u, self.sd_v, self.sd_w)

        u, y = u[self.burnout:], y[self.burnout:]  # Remove burnout

        u = u.reshape(self.ntotbatch, 1, self.seq_len)
        y = y.reshape(self.ntotbatch, 1, self.seq_len)
        return u.astype(np.float32), y.astype(np.float32)

    @property
    def data_shape(self):
        return (1, self.seq_len), (1, self.seq_len)

    def __len__(self):
        return self.ntotbatch

    def __getitem__(self, idx):
        return self.u[idx, ...], self.y[idx, ...]

    @staticmethod
    def _nonlinear_function(y1, y2, u1, u2):
        return (0.8 - 0.5 * np.exp(-y1 ** 2)) * y1 - (0.3 + 0.9 * np.exp(-y1 ** 2)) * y2 \
               + u1 + 0.2 * u2 + 0.1 * u1 * u2

    def _generate_random_input(self, n, nrep, sd=1):
        u = sd*self.rng.randn(int(n//nrep))
        return np.repeat(u, nrep)

    def _simulate_system(self, u, sd_v, sd_w):
        n = np.shape(u)[0]
        v = sd_v * self.rng.randn(n)
        w = sd_w * self.rng.randn(n)
        y = rd.randn(n)
        for k in range(2, n):
            y[k] = self._nonlinear_function(y[k - 1], y[k - 2], u[k - 1], u[k - 2]) + v[k]
        return y + w


if __name__ == "__main__":
    from torch.utils.data import DataLoader
    loader = DataLoader(ChenDataset(seq_len=5, ntotbatch=1000), batch_size=4,
                        shuffle=True, num_workers=4)
    for d in loader:
        print(d)
        quit()
