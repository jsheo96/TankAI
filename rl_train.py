import gym
from stable_baselines3 import A2C
from environment import CustomEnv

env = CustomEnv('282157e777c116c48f482b49b7767f4789cadc4d94ef154e0c5231f24bc2ad59')
#env = gym.make('CartPole-v1')

model = A2C('MlpPolicy', env, verbose=1) #MlpPolicy
model.learn(total_timesteps=1)
model.save("a2c_mlp")
print('model saved')
del model
model = A2C.load("a2c_mlp")
print('model loaded')
obs = env.reset()
for i in range(10):
    action, _state = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
        obs = env.reset()
