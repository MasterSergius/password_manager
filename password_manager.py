#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import simplecrypt

from getpass import getpass
from glob import glob
from optparse import OptionParser
from time import sleep


class PasswordManager(object):
    """ Class for managing your passwords in a safe way """

    def __init__(self):
        self._pass_storage = None
        self._storage_password = None
        self._storage_filename = None

    def _set_new_password(self):
        """ Set new password. Succeed only if password retyped correctly """
        while True:
            password = getpass('Enter new password: ')
            retyped = getpass('Retype new password: ')
            if password == retyped:
                break
            else:
                print 'Password mismatch. Try again'
        return password

    def new_storage(self):
        """ Create new storage by saving empty dict in a new file """
        try:
            filename = raw_input('Enter filename for new storage: ')
            password = self._set_new_password()
            data = simplecrypt.encrypt(password, {})
            with open("%s.pwdm" % filename, 'w') as f:
                f.write(data)
            self._pass_storage = {}
            self._storage_password = password
            self._storage_filename = filename
        except Exception as e:
            print 'Unexpected error: %s' % e
        print 'New password storage created successfully. Now you can add passwords.'

    def change_storage_password(self):
        """ Change storage password """
        if not self._pass_storage:
            print "You must load storage from file or create new."
            return None
        key = getpass('Enter old password: ')
        try:
            data = simplecrypt.decrypt(key, self._pass_storage)
        except:
            print "Wrong password!"
            return None
        password = self._set_new_password()
        save_storage()
        print 'Password changed successfully.'

    def load_storage(self, filename):
        """ Load password storage from file """
        if not filename.endswith(".pwdm"):
            filename += ".pwdm"
        with open(filename, 'r') as f:
            data = f.read()
        self._pass_storage = self._decrypt_storage(data)
        if not self._pass_storage is None:
            self._storage_filename = filename
            return True

    def save_storage(self):
        """ Save password storage to file """
        data = json.dumps(self._pass_storage)
        data = simplecrypt.encrypt(self._storage_password, data)
        with open(self._storage_filename, 'w') as f:
            f.write(data)

    def _decrypt_storage(self, data):
        """ Decrypt password storage by user password """
        key = getpass()
        try:
            data = simplecrypt.decrypt(key, data)
        except:
            print "Wrong password!"
            return False
        else:
            self._storage_password = key
            return json.loads(data)
        return None

    def get_pass_list(self):
        """ Returns all descriptions to stored passwords """
        if not self._pass_storage is None:
            if self._pass_storage:
                for description in self._pass_storage.keys():
                    print description
            else:
                print 'Your password storage is empty'
        else:
            print "You must load storage from file or create new."

    def get_password_by_description(self, desc):
        """ Returns all passwords, which match description pattern """
        passwords = {}
        if not self._pass_storage is None:
            if len(desc) > 100:
                print "Too long description. Try again"
            else:
                for key in self._pass_storage:
                    if desc in key:
                        passwords[key] = self._pass_storage[key]
        return passwords

    def add_new_password(self):
        if self._pass_storage is None:
            print "You must load storage from file or create new."
            return None

        while True:
            description = raw_input('Enter description (up to 100 symbols): ')
            if len(description) > 100:
                print "Too long description. Try again"
            elif description in self._pass_storage:
                print "This description exists already in current storage"
            else:
                break
        password = self._set_new_password()
        self._pass_storage[description] = password
        print "New password successfully added! To save it use command 'save'."

    def del_password(self):
        if self._pass_storage is None:
            print "You must load storage from file or create new."
            return None

        if not self._pass_storage:
            print 'Your password storage is empty'
            return None

        counter = 0
        while True:
            description = raw_input('Enter description (up to 100 symbols): ')
            if len(description) > 100:
                print "Too long description. Try again"
            else:
                for key in self._pass_storage.keys():
                    if description in key:
                        del self._pass_storage[key]
                        counter += 1
                break
        print "Deleted %s passwords." % counter
        print "You can quit without saving to restore deleted passwords."

def list_files(extension):
    """ Returns list of files with specified extension in current directory """
    return glob('*.%s' % extension)

def menu():
    """Password Manager v1.0 by MasterSergius <master.sergius@gmail.com>

    Commands:
        * 'help' - print this help string
        * 'ls' - print list of all *.pwdm files in current directory
        * 'new' - create new password storage
        * 'load' <filename> - load passwords from file <filename>
        * 'save' <filename> - save passwords to file <filename>
        * 'show' - show keywords for passwords in current file
        * 'get' <keyword> - show password for <keyword>
        * 'add' - add new pair (keyword, password)
        * 'del' <keyword> - delete connected pair (keyword, password)
        * 'exit' or 'quit' - exit (hit Ctrl+C if program stuck)

    * NOTE*: You can specify different passwords for different files.
             Password for file stores in that file.

    Example:
        pwdm > load work.pwdm
        Enter password: <type password>
        Load password file successfully
        pwdm > show
        my computer
        office mail
        domain password
        mysql admin
        pwdm > get my
        my computer - qwerty
        mysql admin - admin
    """
    print menu.__doc__
    pwdm = PasswordManager()

    while True:
        cmd = raw_input('pwdm > ')
        cmd = cmd.strip().split()
        if not cmd:
            continue

        if cmd[0] == 'help':
            print menu.__doc__

        elif cmd[0] == 'ls':
            ls = list_files('pwdm') or []
            for fname in ls:
                print fname

        elif cmd[0] == 'new':
            pwdm.new_storage()

        elif cmd[0] == 'load':
            success = None
            try:
                success = pwdm.load_storage(cmd[1])
            except IndexError:
                print 'You must specify storage filename'
            except Exception as e:
                print 'Error loading storage: %s' % e
            if success:
                print 'Password storage loaded successfully.'

        elif cmd[0] == 'save':
            try:
                pwdm.save_storage()
            except Exception as e:
                print 'Error saving storage: %s' % e
            else:
                print 'Password storage saved successfully.'

        elif cmd[0] == 'add':
            pwdm.add_new_password()

        elif cmd[0] == 'del':
            pwdm.del_password()

        elif cmd[0] == 'show':
            pwdm.get_pass_list()

        elif cmd[0] == 'get':
            passw = None
            try:
                passw = pwdm.get_password_by_description(cmd[1])
            except IndexError:
                # Get all passwords if no keyword specified
                passw = pwdm.get_password_by_description('')
            except Exception as e:
                print 'Error getting password by key: %s' % e
            if passw:
                for key in passw:
                    print "%s - %s" % (key, passw[key])
            else:
                print 'No passwords with that description'


        elif cmd[0] in ('exit', 'quit'):
            break


if __name__ == '__main__':
    menu()
