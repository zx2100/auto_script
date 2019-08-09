#!/root/python/env/bin/python

import pexpect

def main():
    child = pexpect.spawn("/usr/bin/ssh root@localhost")

    index = child.expect(["yes/no", pexpect.exceptions.EOF, pexpect.TIMEOUT], timeout=5)
    if index == 0:
        child.sendline("yes")
        child.expect(["yes/no", pexpect.exceptions.EOF, pexpect.TIMEOUT], timeout=5)
    else:
        return

if __name__ == "__main__":
    main()
