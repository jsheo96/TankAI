import gym
from stable_baselines3 import PPO
import yaml
env = gym.make('MiniGrid-DoorKey-5x5-v0')
kwargs = yaml.load(open('hyperparams/ppo.yaml','r'), Loader=yaml.FullLoader)['MiniGrid-DoorKey-5x5-v0']
model = PPO(env=env, verbose=1, **kwargs)
model.learn(total_timesteps=100000)
model.save("models/ppo_mlp")
print('model saved')
del model
model = PPO.load("models/ppo_mlp")
print('model saved')
obs = env.reset()
for i in range(1000):
    action, _state = model.predict(obs, deterministic=True)
    print(_state)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
      obs = env.reset()
