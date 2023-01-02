import torch
import numpy as np
from src.modules.layers_u2net.u2net import U2NET


class U2NETHelper:
    def __init__(
        self, model_path: str, device: torch.device = torch.device("cuda")
    ) -> None:
        self.device = device
        self.model = U2NET(3, 1)
        self.model.load_state_dict(torch.load(model_path))
        self.model.to(device)
        self.model.eval()

    def _normPRED(self, d: torch.Tensor):
        ma = torch.max(d)
        mi = torch.min(d)
        dn = (d - mi) / (ma - mi)
        return dn

    def inference(self, input: np.ndarray):
        # normalize the input
        tmpImg = np.zeros((input.shape[0], input.shape[1], 3))
        input = input / np.max(input)
        tmpImg[:, :, 0] = (input[:, :, 2] - 0.406) / 0.225
        tmpImg[:, :, 1] = (input[:, :, 1] - 0.456) / 0.224
        tmpImg[:, :, 2] = (input[:, :, 0] - 0.485) / 0.229

        # convert BGR to RGB
        tmpImg = tmpImg.transpose((2, 0, 1))
        tmpImg = tmpImg[np.newaxis, :, :, :]
        tmpImg = torch.from_numpy(tmpImg)

        # convert numpy array to torch tensor
        tmpImg = tmpImg.type(torch.FloatTensor)

        if torch.cuda.is_available():
            tmpImg = tmpImg.cuda()
        else:
            tmpImg = tmpImg

        # inference
        d1, d2, d3, d4, d5, d6, d7 = self.model(tmpImg)

        # normalization
        pred = d1[:, 0, :, :]
        pred = self._normPRED(pred)
        # convert torch tensor to numpy array
        pred = pred.squeeze()
        pred = pred.cpu().data.numpy()

        del d1, d2, d3, d4, d5, d6, d7

        return pred