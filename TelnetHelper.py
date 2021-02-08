import telnetlib
import time
import logging
import re


class TelnetHelper:
    def __init__(self):
        self.tn = telnetlib.Telnet()

    def login(self, ip, port):
        try:
            self.tn.open(ip, port, timeout=3)
        except Exception as e:
            print('Error: TelnetHelper.login - %s' % e)
            return

        self.tn.read_until(b"Login:")  # 当反馈信息出现“Login:“时，等待……
        username = input(">>>Username：")
        self.tn.write(username.encode("ascii") + b"\n")  # 将用户名传入
        time.sleep(1)
        if "The user does not exist!" in self.tn.read_very_eager().decode("ascii"):
            logging.warning("用户名不存在")
            time.sleep(1)
            self.tn.close()
            return False
        else:
            self.tn.read_until(b"Dynamic SMS: ")  # 当反馈信息出现“Dynamic SMS: “时，等待……
            password = input(">>>Dynamic SMS:")
            self.tn.write(password.encode("ascii") + b"\n")  # 将验证码传入
            time.sleep(2)
            if "Login success !" not in self.tn.read_very_eager().decode("ascii"):
                logging.warning("验证码有误")
                time.sleep(1)
                self.tn.close()
                return False
            else:
                print('%s登录成功' % ip)
                time.sleep(0.5)
                print("")
                print("-" * 20 + "指令执行中" + "-" * 20)
                time.sleep(1)
                return True

    def login_device(self, device_ip):
        """选择路由器序号和从账号并登录"""
        self.tn.read_until(b"Please enter your choice: ", timeout=5)
        self.tn.write('2'.encode('utf-8') + b"\n")  # 选第二项（根据实际反馈选择）
        self.tn.read_until(b'Please enter the device ip or No: ', timeout=5)
        self.tn.write(device_ip.encode('utf-8') + b"\n")
        self.tn.read_until(b'Please enter the slave account or No: ', timeout=5)
        self.tn.write(b'0\n')  # 选择从账号
        self.tn.read_until(b'#(GBA) into interactive mode. Congratulation!', timeout=10)
        self.tn.write(b'screen-length 0 temporary\n')

    def run_command(self, command):
        self.tn.write(b"\n")
        self.tn.write(command.encode('ascii') + b'\n')
        time.sleep(0.5)
        # print(command)
        result = ''
        while True:
            every_loop_result = self.tn.read_very_eager()
            if every_loop_result != b'':
                result += every_loop_result.decode('gbk')
                time.sleep(0.5)
            else:
                break
        return result

    def run(self, ip, port):
        """主运行程序"""
        #  判断登录函数布尔值，仅当返回True时继续执行
        if self.login(ip, port) is True:
            with open('result.txt', 'w') as f:
                devices = [('RT05/06', ('218.201.141.9', '218.201.141.10')),
                            ('RT07/08', ('111.17.251.209', '111.17.251.210')),
                            ('RT09/10', ('111.17.251.216', '111.17.251.217')),
                            ('RT11/12', ('111.17.251.222', '111.17.251.223')),
                            ('RT13/14', ('111.17.251.225', '111.17.251.226')),
                            ('RT15/16', ('111.17.251.228', '111.17.251.229')),
                            ('RT17/18', ('111.17.251.242', '111.17.251.243'))]
                for (bras_name, (a_ip, b_ip)) in devices:
                    self.login_device(a_ip)
                    olt_lst_from_a = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                                                self.run_command('display access-user domain olt-guanli normal'))

                    self.run_command('quit')
                    time.sleep(0.5)

                    self.login_device(b_ip)
                    olt_lst_from_b = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                                                self.run_command('display access-user domain olt-guanli normal'))
                    self.run_command('quit')
                    time.sleep(0.5)

                    result = "%s:   " % bras_name
                    if olt_lst_from_a or olt_lst_from_b:
                        result += "异常地址： %s" % ', '.join(olt_lst_from_a + olt_lst_from_b)
                    else:
                        result += "OLT管理检查无异常"

                    print(result)
                    f.write(result + '\n')

            print("-" * 20 + "操作已完成" + "-" * 20)
            input("输入回车离开 >")


def main():
    thelper = TelnetHelper()
    thelper.run('10.213.47.197', 9023)


if __name__ == '__main__':
    main()