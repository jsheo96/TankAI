from stable_baselines3 import PPO
from simplest_cnn_simulator import CustomEnv
from stable_baselines3.ppo.policies import CnnPolicy
from custom_network import CustomCNN
from stable_baselines3.common.env_util import make_vec_env
import yaml
# env = CustomEnv()
env = make_vec_env(CustomEnv, n_envs=8)
policy_kwargs = dict(
    features_extractor_class=CustomCNN
)
kwargs = yaml.load(open('hyperparams/ppo_multiinput.yaml','r'), Loader=yaml.FullLoader)['MiniGrid-DoorKey-5x5-v0']
model = PPO(env=env, verbose=1, policy_kwargs=policy_kwargs, **kwargs)
model.learn(total_timesteps=200000)
model.save("models/simplest_ppo_cnn")
print('model saved')
del model
model = PPO.load("models/simplest_ppo_cnn")
print('model loaded')
env = CustomEnv()
obs = env.reset()
for i in range(1000):
    action, _state = model.predict(obs, deterministic=True)
    print(action)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
      obs = env.reset()
