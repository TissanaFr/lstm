from subprocess import Popen
import os

# example:
# 'python {0} --user {1} --cand {2} --pwd {3} --m 50'.format(
#         os.path.join(cur_dir, 'parse_fb_ad.py'), my_email@mail.com, os.path.join(cur_dir, 'candidates-1.txt'),
#         pa$$w0rD)

cur_dir = os.getcwd()
commands = [
    'python {0} --user {1} --cand {2} --pwd {3} --m 50'.format(
        os.path.join(cur_dir, 'parse_fb_ad.py'), your_email1, os.path.join(cur_dir, 'candidates-1.txt'), your_password1),
    'python {0} --user {1} --cand {2} --pwd {3} --m 50'.format(
        os.path.join(cur_dir, 'parse_fb_ad.py'), your_email2, os.path.join(cur_dir, 'candidates-2.txt'), your_password2),
]
# run in parallel
processes = [Popen(cmd, shell=True) for cmd in commands]

for p in processes:
    p.wait()
