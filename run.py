import os
import time
import winreg
import random
import requests
from typing import Optional, Union

class Launcher:
    def __init__(self) -> None:
        self.process_name = "RobloxPlayerBeta"
        self.auth_url = "https://auth.roblox.com/v1/authentication-ticket/"
        self.false_tracker = self.create_false_tracker()
        self.launch_time = int(time.time()*1000)
        self.session = requests.session()


    def get_launcher(self) -> str:
        '''
            Fetches the launcher path from the registry.
            
            Returns:
                (str): Path to the launcher.
        '''
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\roblox\DefaultIcon") as key:
            data = winreg.QueryValueEx(key, "")[0]
        return data
 

    def create_false_tracker(self) -> str:
        '''
            For -b flag, creates a random number to substitute as the browser tracker.

            Returns:
                (str): Random number.
        '''

        return str(random.randint(100000, 900000))


    def authenticate_join(self) -> Union[str, dict]:
        '''
            Gets ticket for -t flag, requires cookie and X-CSRF which we can grab from sending a request then retrieving out of the headers.

            Returns:
                ([str, dict]): Authentication ticket or response json.
        '''
        try:
            resp = self.session.post(self.auth_url)
            headers = { 
                "Referer": "https://www.roblox.com/home",
                "x-csrf-token": resp.headers["X-CSRF-Token"]
            }
            resp = self.session.post(self.auth_url, headers=headers)

            return resp.headers['rbx-authentication-ticket']
        except KeyError:
            return resp.json()        


    def get_launch_args(self, auth, place) -> str:
        '''
            Creates launch args for direct execution, will return false if KeyError is encountered while attempting to retrieve the auth ticket.

            Returns:
                (str): Launch args.
        '''

        return f"--app -t \"{auth}\" "\
        f"-j \"https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame&browserTrackerId={self.false_tracker}&placeId={place}&isPlayTogetherGame=false\" "\
        f"-b \"{self.false_tracker}\" --launchtime={self.launch_time} --rloc \"en_us\" --gloc \"en_us\" "


    def launch_client(self, cookie, placeId) -> Optional[str]:
        '''
            Launches the client.

            Returns:
                (str): Error if encountered.
        '''
        if not cookie:
            return "No cookie provided"
        if not placeId:
            return "No place ID provided"

        self.session.cookies['.ROBLOSECURITY'] = cookie
        auth = self.authenticate_join()

        path = self.get_launcher()
        path = path.replace("RobloxPlayerLauncher.exe", "RobloxPlayerBeta.exe")

        if not path:
            return "Could not find RobloxPlayerBeta.exe"

        if type(auth) is dict:
            return auth.get('errors')[0]
        else:
            launch_args = self.get_launch_args(auth, placeId)
            cmd = f"start \"\" \"{path}\" {launch_args}"
            os.system(cmd)


if __name__ == "__main__":
    account = input("Account Cookie: ")
    place = input("Place ID: ")

    launcher = Launcher()
    errors = launcher.launch_client(account, place)
    
    if errors:
        print(errors)
