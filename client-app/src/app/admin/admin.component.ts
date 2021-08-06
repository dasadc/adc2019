import { Component, OnInit } from '@angular/core';
import { Observable, of, from } from 'rxjs';
import { catchError, map, tap, flatMap, filter } from 'rxjs/operators';

import { AdcService } from '../adc.service';
import { ResTimekeeper, AdminQList, ResUserInfo, ResMsgOnly } from '../apiresponse';

import * as yaml from 'js-yaml';

class UserInfo extends ResUserInfo {
  constructor(
    public username: string,
    public displayname: string,
    public uid: number,
    public gid: number,
    public selected: boolean = false
  ) {
    super(username, displayname, uid, gid);
  }
  static from_ResUserInfo(o: ResUserInfo): UserInfo {
    return new UserInfo(o.username, o.displayname, o.uid, o.gid);
  }
};

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  tk: ResTimekeeper;
  tk_enabled_values = [0, 1];
  tk_state_values = ['init', 'im0', 'Qup', 'im1', 'Aup', 'im2'];
  enabledDescrTbl = ResTimekeeper.enabledDescrTbl;
  stateDescrTbl = ResTimekeeper.stateDescrTbl;
  adminQList: AdminQList;
  adminQListText: string;
  testMode: boolean;
  viewScoreMode: boolean;
  adminQAll: Object;
  adminAAll: Object;
  //userList: string[];
  userInfoList: UserInfo[] = [];  // Object[] = [];
  uploadResults: string;
  title: string = 'ADC Administration';

  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.adcService.version()
      .subscribe((ver: number) => {
        this.title = `ADC${ver} Administration`;
      });
    this.getTimekeeper();
    this.getTestMode();
    this.getViewScoreMode();
    this.getUserList();
  }

  timekeeper_enabled(i: number) {
    //console.log('enabled', i);
    this.tk.enabled = i;
    this.setTimekeeper();
  }

  timekeeper_state(state: string) {
    //console.log('state', state);
    this.tk.state = state;
    this.setTimekeeper();
  }

  getTimekeeper() {
    this.adcService.getTimekeeper()
      .subscribe(tk => {
        this.tk = tk;
      });
  }

  setTimekeeper() {
    this.adcService.setTimekeeper(this.tk)
      .subscribe(tk => {
        //console.log('admin: setTimeKeeper: tk=', tk);
        this.tk = tk;
      });
  }

  testModeIsDefined(): boolean {
    return this.testMode !== void 0;
  }

  getTestMode() {
    //console.log('getTestMode');
    this.adcService.getTestMode()
      .subscribe(res => {
        //console.log('admin getTestMode', res);
        this.testMode = res;
      });
  }

  setTestMode(value: boolean) {
    //console.log('setTestMode', value);
    this.adcService.setTestMode(value)
      .subscribe(res => {
        //console.log('admin setTestMode', res);
        this.testMode = res;
      });
  }

  viewScoreModeIsDefined(): boolean {
    return this.viewScoreMode !== void 0;
  }

  getViewScoreMode() {
      //console.log('getViewScoreMode');
      this.adcService.getViewScoreMode()
        .subscribe(res => {
          //console.log('admin getViewScoreMode', res);
          this.viewScoreMode = res;
        });
    }

    setViewScoreMode(value: boolean) {
      //console.log('setViewScoreMode', value);
      this.adcService.setViewScoreMode(value)
        .subscribe(res => {
          //console.log('admin setViewScoreMode', res);
          this.viewScoreMode = res;
        });
    }

  getAdminQList(event: Object) {
    //console.log('get', event);
    let full: boolean = !event['altKey'] && event['ctrlKey'] && event['shiftKey'];
    this.adcService.getAdminQList()
      .subscribe(res => {
        if (res) {
          this.adminQList = res;
          this.adminQListText = full ? res.text_admin : res.text_user;
        }
      });
  }

  deleteAdminQList(event: Object) {
    //console.log('delete', event);
    let mod: boolean = event['altKey'] && event['ctrlKey'] && event['shiftKey'];
    //console.log('delete mod', mod);
    if (mod) {
      this.adcService.deleteAdminQList()
        .subscribe(res => {
          //console.log('res=', res);
          this.adminQListText = res['msg'];
        });
    }
  }

  putAdminQList(event: Object) {
    //console.log('put', event);
    let mod: boolean = !event['altKey'] && !event['ctrlKey'] && event['shiftKey'];
    //console.log('put mod', mod);
    if (mod) {
      this.adcService.putAdminQList()
        .subscribe(res => {
          //console.log('res=', res);
          // this.adminQListText = res['msg']; // show admin Q list
          this.adminQListText = 'created.';
        });
    }
  }


  getAdminQAll(event: Object) {
    let mod: boolean = !event['altKey'] && event['ctrlKey'] && event['shiftKey'];
    if (mod) {
      this.adcService.getAdminQAll()
        .subscribe(res => {
          if (res) {
            //console.log(res);
            this.adminQAll = res;
          }
        });
    }
  }

  deleteAdminQAll(event: Object) {
    let mod: boolean = event['altKey'] && event['ctrlKey'] && event['shiftKey'];
    if (mod) {
      this.adcService.deleteAdminQAll()
        .subscribe(res => {
          if (res) {
            //console.log(res);
            this.adminQAll = undefined;
          }
        });
    }
  }


  getAdminAAll(event: Object) {
    let mod: boolean = !event['altKey'] && event['ctrlKey'] && event['shiftKey'];
    if (mod) {
      this.adcService.getAdminAAll()
        .subscribe(res => {
          if (res) {
            //console.log(res);
            this.adminAAll = res;
          }
        });
    }
  }

  deleteAdminAAll(event: Object) {
    let mod: boolean = event['altKey'] && event['ctrlKey'] && event['shiftKey'];
    if (mod) {
      this.adcService.deleteAdminAAll()
        .subscribe(res => {
          if (res) {
            //console.log(res);
            this.adminAAll = undefined;
          }
        });
    }
  }

  /*
  getUserList(event?: Object) {
    this.userInfoList = [];
    this.adcService.getUserList()
      .subscribe(res => {
        this.userList = res;
      	for (let i=0; i<this.userList.length; i++) {
      	  let userName = this.userList[i];
      	  this.adcService.getUserInfo(userName)
      	    .subscribe(res2 => {
      	      //console.log('res2=', res2);
              if (res2['msg'] !== void 0) {
                let tmp = res2['msg'].split(':');
        	      this.userInfoList.push({'username': tmp[0],
        				  'displayname': tmp[1],
        				  'uid': tmp[2],
        				  'gid': tmp[3],
                  'selected': false});
              }
      	    });
      	} // for i
      });
  }
  */

  userInfoList_sort() {
    this.userInfoList.sort((a, b) => {return a.uid - b.uid});
    return this.userInfoList;
  }

  getUserList(event?: Object) {
    this.userInfoList = [];
    this.adcService.getAllUserInfo()
      .subscribe((x: ResUserInfo) => {
        //console.log('getUserList x', x);
        this.userInfoList.push(UserInfo.from_ResUserInfo(x));
      });
  }

  deleteCheckedUsers($event) {
    let mod: boolean = event['altKey'] && event['ctrlKey'] && event['shiftKey'];
    if (mod) {
      //console.log('deleteCheckedUsers', this.userInfoList);
      from(this.userInfoList)
        .pipe(
          filter((u: UserInfo) => u.selected),
          flatMap((u: UserInfo) => {
            //return of(u['username']);
            return this.adcService.deleteUserInfo(u.username);
          })
        )
        .subscribe(
          (res: Object) => {
            if (res['msg'] !== void 0) {
              console.log(res['msg']);
            }
          },
          (err: Object) => {
            console.log('ERROR', err);
          },
          () => { // 完了したとき
            this.getUserList();
          }
        );
      /*
      for (let i=0; i<this.userInfoList.length; i++) {
        if (this.userInfoList[i]['selected']) {
          let user = this.userInfoList[i]['username'];
          //console.log('To delete', user);
          this.adcService.deleteUserInfo(user)
            .subscribe(
              (res: Object) => {
                if (res['msg'] !== void 0) {
                  console.log(res['msg']);
                  // this.getUserList(); //これは、this.userInfoListを上書きしてしまうのでうまくいかない
                }
              },
              (err: Object) => {
              },
            );
        }
      }
      // TODO すべて削除が完了したあとで、ユーザーリストの表示を更新したい。
      */
    }
  }

  postUsersYamlFile(f: Object) {
    //console.log('postUsersYamlFile');
    //console.log('filename', f['filename']);
    //console.log('text', f['text']);
    if (f['filename'] === void 0 || f['text'] === void 0) {
      return;
    }
    let users = yaml.load(f['text']) as Object[];
    from(users)
      .pipe(
        flatMap((user: Object) => {
          //console.log('postUsersYamlFile: user=', user);
          return this.adcService.createUser(user);
        })
      )
      .subscribe(
        (res: ResMsgOnly) => {
          if (res.msg !== void 0) {
            console.log('postUsersYamlFile ', res.msg);
          } else { // error
            console.log('postUsersYamlFile ERROR', res);
          }
        },
        (err) => console.log('postUsersYamlFile ERROR err=', err),
        () => {
          //console.log('complete');
          this.getUserList();
        }
      );
    /*
    //console.log(o);
    for (let i=0; i<o.length; i++) {
      console.log('postUsersYamlFile', i, o[i]);
      this.adcService.createUser(o[i])
        .subscribe(res => {
          if (res['msg'] !== void 0) {
            console.log('postUsersYamlFile ', res['msg']);
          } else { // error
            console.log('postUsersYamlFile ', res);
          }
        });
    }
    */

    /*
    let username: string = this.adcService.getUsername();
    this.adcService.postUserQ(username, this.postQNumber, f['text'], f['filename'])
      .subscribe(
        (res: string) => {
        //console.log('res=', res);
        this.uploadResults = res;
        this.getUserQList();
      },
      (res: string) => {
        //console.log('ERROR', res);
        this.uploadResults = res;
      });
    */
  }

  onCleared(c: boolean) {
    console.log('upload-yaml onCleared', c)
  }
}
