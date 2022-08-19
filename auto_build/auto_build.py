import os
import yaml
import time
import shutil
import paramiko
import platform
from urllib import parse
from git.repo import Repo
from datetime import datetime


class AutoBuild:
    def __init__(self):
        self.values = self.read_yaml()
        self.temp_path = []  # 暂存文件路径列表
        self.git_repo_url = self.values.get("git_repo_url")
        self.branch = self.values.get("branch")
        self.repo_login_username = parse.quote(self.values.get("repo_login_username"))
        self.repo_login_passwd = parse.quote(self.values.get("repo_login_passwd"))
        self.rm_or_cp = self.values.get("rm_or_cp")
        self.target_clone_path = str(self.values.get("target_clone_path")).replace('\\', '/')
        self.build_order = self.values.get("build_order")
        self.jar_name = self.values.get("jar_name")
        self.target_host = self.values.get("target_host")
        self.host_user_name = self.values.get("host_user_name")
        self.host_passwd = self.values.get("host_passwd")
        self.tar_publish_path = self.values.get("tar_publish_path")
        self.publish_exec_script = self.values.get("publish_exec_script")
        self.docker_file = self.values.get("docker_file")

    # 读取yaml文件
    def read_yaml(self):
        with open(file="./env.yaml", mode='r', encoding='utf-8') as file:
            values = yaml.load(stream=file, Loader=yaml.FullLoader)
            return values

    # window下若存在只读文件，需强制删除
    def remove_file(self, path):
        if 'windows' == platform.system().lower():
            while True:
                try:
                    shutil.rmtree(path)
                except Exception as err:
                    # print("error:", str(err))
                    only_read_file = str(err).split("。: ")[1].strip(" '").strip("' ").strip("'").strip(" ")
                    print('强制删除只读文件:', only_read_file)
                    os.system('del "{path}" /F'.format(path=only_read_file))
                    # os.unlink(only_read_file)
                if not os.path.exists(path):
                    break
        elif 'linux' == platform.system().lower():
            os.system('rm -rf %s' % path)

    # 找出目标文件
    def get_if_dir(self, file_path, tar_file_name):
        temp_list = os.listdir(file_path)
        for temp in temp_list:
            path = file_path + '\\' + temp
            if os.path.isfile(path):
                if tar_file_name == os.path.split(path)[-1]:
                    self.temp_path.append(path)
                else:
                    continue
            else:
                self.get_if_dir(path, tar_file_name)

    # 拉取代码
    def clone_code(self):
        if not os.path.exists(self.target_clone_path):
            print("%s> 文件夹不存在，创建目标文件夹" % ('=' * 10,))
            os.mkdir(self.target_clone_path)
        if 0 != len(os.listdir(self.target_clone_path)):
            if 1 == self.rm_or_cp:
                print("%s> 非空文件夹，玩命清空中。。。" % ('=' * 10,))
                self.remove_file(self.target_clone_path)
            else:
                print("%s> 非空文件夹，玩命备份中。。。" % ('=' * 10,))
                now_time = str(datetime.now().strftime('%Y%m%d%H%M%S'))[2:]
                os.rename(self.target_clone_path, self.target_clone_path + '.bak' + now_time)
                os.mkdir(self.target_clone_path)

        # 克隆代码，gitpython克隆格式：http://uname:passwd@repo_url
        urls = self.git_repo_url.split('//')
        git_url = urls[0] + '//' + self.repo_login_username + ':' + self.repo_login_passwd + '@' + urls[1]
        print("git_url：", git_url)
        Repo.clone_from(url=git_url, to_path=self.target_clone_path, branch=self.branch)
        print('%s> 拉取代码成功' % ('=' * 10,))

    # 构建并获取目标jar包
    def build_jar(self):
        self.get_if_dir(self.target_clone_path, 'pom.xml')
        tar_pom = min(self.temp_path)
        print('%s> 开始构建' % ('=' * 10,))
        # # way1 & way2
        # os.system('mvn clean package -f %s' % str(tar_pom))
        try:
            tar_pom_path = os.path.split(tar_pom)[0]
            if 'windows' == platform.system().lower():
                root_path = str(tar_pom_path).split(':')[0] + ':'
                # os.system('{0} & cd "{1}" & chdir & {2}'.format(root_path, tar_pom_path, self.build_order))
            elif 'linux' == platform.system().lower():
                os.system('cd "{0}" && pwd && {1}'.format(tar_pom_path, self.build_order))
        except Exception as err:
            print(err)
        else:
            print("%s> 构建成功" % ('=' * 10,))
            # self.temp_path = []  # 清空暂存文件路径列表
            self.get_if_dir(file_path=self.target_clone_path, tar_file_name=self.jar_name)
        print("xxxxxxxxxxx:", self.temp_path)
        return min(self.temp_path)

    # 发布
    def publish_jar(self, jar_path=None):
        print("%s> 开始发布" % ('=' * 10,))
        try:
            trans = paramiko.Transport((self.target_host, 22))
            trans.connect(username=self.host_user_name, password=self.host_passwd)
            # 建立sftp连接 & 命令连接
            sftp = paramiko.SFTPClient.from_transport(trans)
            ssh = paramiko.SSHClient()
            ssh._transport = trans
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许不在know_host中的主机连接

            # 格式化发布路径
            if '/' != str(self.tar_publish_path)[-1]:
                remote_path = self.tar_publish_path + '/'
            else:
                remote_path = str(self.tar_publish_path)

            # 备份原有jar包
            tar_mv = remote_path + '*.' + str(self.jar_name).split('.')[-1]
            pre_cmd = '''
                if [ ! -d "{0}" ];  then mkdir {0};echo "创建发布路径成功"; fi &&
                if [ ! -d "{1}" ];  then mkdir {1};echo "创建备份路径成功"; fi &&
                if [ -f {2} ];  then mv {3} {1};echo "移动备份jar包成功"; fi
            '''.format(remote_path, remote_path + 'jar_bak', remote_path + self.jar_name, tar_mv)
            pre_stdin, pre_stdout, pre_stderr = ssh.exec_command(pre_cmd)  # 命令输入&输出&异常
            print("pre_stdout: ", pre_stdout.read().decode())
            print("pre_stderr: ", pre_stderr.read().decode())
            # 发送jar包
            sftp.put(localpath=r"{}".format(jar_path), remotepath=remote_path + self.jar_name)
            # 发布
            # 先验目标路径是否已有执行脚本等
            pre_publish_cmd = '''
                if [ -f {0} ] && [ -f {1} ];  then echo "True"; else echo "False"; fi
                '''.format(remote_path + self.publish_exec_script, remote_path + self.docker_file)
            pub_stdin, pub_stdout, pub_stderr = ssh.exec_command(pre_publish_cmd)
            temp_pub_stdout = pub_stdout.read().decode()
            print('pub_stdout:', temp_pub_stdout)
            print('pub_stderr:', pub_stderr.read().decode())
            if 'T' == temp_pub_stdout[0]:
                print('%s> 执行脚本及Dockerfile同时存在，无需上传' % ("=" * 10))
            elif 'F' == temp_pub_stdout[0]:
                print('%s> 执行脚本及Dockerfile未同时存在，正在上传' % ("=" * 10))
                sftp.put(localpath=r"./{}".format(self.publish_exec_script),
                         remotepath=remote_path + self.publish_exec_script)
                sftp.put(localpath=r"./{}".format(self.docker_file), remotepath=remote_path + self.docker_file)
            # 执行启动脚本
            publish_cmd = "cd {0} && chmod +x {1} && sh {1}".format(self.tar_publish_path, self.publish_exec_script)
            end_stdin, end_stdout, end_stderr = ssh.exec_command(publish_cmd)
            print("end_stdout: ", end_stdout.read().decode())
            print("end_stderr: ", end_stderr.read().decode())
            print('%s> 发布完毕' % ('=' * 10,))
            # 查看是否启动成功
            time.sleep(20)
            test_stdin, test_stdout, test_stderr = ssh.exec_command("docker ps")
            print("test_stdout:\n", test_stdout.read().decode())
            print("test_stderr:", test_stderr.read().decode())
        finally:
            trans.close()

    def run(self):
        if len(self.target_clone_path) > 4:
            # self.clone_code()
            jar_path = self.build_jar()
            # print("jar_path:", jar_path)
            # self.publish_jar(jar_path)
        else:
            print('target_clone_path: 请不要指定根目录！！！')


if __name__ == '__main__':
    ab = AutoBuild()
    ab.run()
