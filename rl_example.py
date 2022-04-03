import gym
from stable_baselines3 import A2C

env = gym.make('CartPole-v1')

model = A2C('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=1)
model.save("a2c_mlp")
print('model saved')
del model
model = A2C.load("a2c_mlp")
print('model saved')
obs = env.reset()
for i in range(10):
    action, _state = model.predict(obs, deterministic=True)
    print(_state)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
      obs = env.reset()
