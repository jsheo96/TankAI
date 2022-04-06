from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch.nn as nn
import gym
import torch

def init_params(m):
    classname = m.__class__.__name__
    if classname.find("Linear") != -1:
        m.weight.data.normal_(0, 1)
        m.weight.data *= 1 / torch.sqrt(m.weight.data.pow(2).sum(1, keepdim=True))
        if m.bias is not None:
            m.bias.data.fill_(0)

class CustomCNN(BaseFeaturesExtractor):
    """
    :param observation_space: (gym.Space)
    :param features_dim: (int) Number of features extracted.
        This corresponds to the number of unit for the last layer.
    """

    def __init__(self, observation_space, features_dim=67):
        super(CustomCNN, self).__init__(observation_space, features_dim)
        self.image_conv = nn.Sequential(
            nn.Conv2d(4, 16, (2, 2)),
            nn.ReLU(),
            nn.MaxPool2d((2, 2)),
            nn.Conv2d(16, 32, (2, 2)),
            nn.ReLU(),
            nn.Conv2d(32, 64, (2, 2)),
            nn.ReLU()
        )
        self.fc1 = nn.Linear(3, 16)
        self.fc2 = nn.Linear(16, 3)
        self.relu = nn.ReLU()
        self.flatten = nn.Flatten()
        self.apply(init_params)

    def forward(self, observations):
        image = observations['image']
        ap = observations['ap']
        hp = observations['hp']
        aim = observations['aim']
        x = image.transpose(1,3).transpose(2,3)
        x = self.image_conv(x)
        x = self.flatten(x)
        y = torch.cat((ap,hp,aim),-1)
        y = self.fc1(y)
        y = self.relu(y)
        y = self.fc2(y)
        y = self.relu(y)
        x = torch.cat((x,y),-1)
        return x

