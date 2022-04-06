from stable_baselines3 import PPO
from simplest_simultor import CustomEnv
import yaml
env = CustomEnv()
kwargs = yaml.load(open('hyperparams/ppo.yaml','r'), Loader=yaml.FullLoader)['MiniGrid-DoorKey-5x5-v0']
model = PPO(env=env, verbose=1, **kwargs)
model.learn(total_timesteps=10000)
model.save("models/simplest_ppo_mlp")
print('model saved')
del model
model = PPO.load("models/simplest_ppo_mlp")
print('model loaded')
obs = env.reset()
for i in range(10000):
    action, _state = model.predict(obs, deterministic=True)
    #print(action)
    obs, reward, done, info = env.step(action)
    # env.render()
    if done:
      obs = env.reset()
