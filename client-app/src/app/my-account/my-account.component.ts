import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
import { ResMsgOnly, ResLogout } from '../apiresponse';
import { AppComponent } from '../app.component';

@Component({
  selector: 'app-my-account',
  templateUrl: './my-account.component.html',
  styleUrls: ['./my-account.component.css']
})
export class MyAccountComponent implements OnInit {
  whoami: string;
  getUser: string;
  changePassword: string;
  username: string;
  logout: string;
  my_api_server: string = '';
  default_api_server: string = '';

  constructor(private adcService: AdcService,
              private appComponent: AppComponent) { }

  ngOnInit() {
    this.username = this.adcService.getUsername();
    this.my_api_server = this.adcService.get_API_server_origin();
    this.default_api_server = location.origin;
  }

  doWhoami(): void {
    //console.log('doWhoami:');
    this.adcService.whoami()
    .subscribe((res: ResMsgOnly) => {
      //console.log('doWhoami: res', res);
      this.whoami = res.msg;
      this.username = res.msg;
    });
    // 開発時のテスト
    /*
    this.adcService.devel_test_01()
    .subscribe((res: string) => {
      console.log('doWhoami: devel_test_01: res', res);
      console.log('origin:', location.origin);
    });
    */
  }

  doGetUser(): void {
    let u = this.adcService.getUsername();
    //console.log('doGetUserInfo:', u);
    if (u === void 0) {
      this.getUser = 'Current user name is undefined. Try click whoami button.';
      return;
    }
    this.adcService.getUserInfo()
    .subscribe((res: ResMsgOnly) => {
      //console.log('doGetUser: res', res);
      this.getUser = res.msg;
    });
  }

  doChangePassword(passwd0:string, passwd1:string, passwd2:string): void {
    //console.log('doChangePassword:', this.username, passwd0, passwd1, passwd2);
    if (passwd1 != passwd2) {
      this.changePassword = 'password mismatch, not changed.'
      return;
    }
    if (passwd1.length < 6) {
      this.changePassword = 'password must be at least six characters.'
      return;
    }
    this.adcService.changePassword(this.username, passwd0, passwd1)
    .subscribe(
      (res: ResMsgOnly) => {
        //console.log('changePassword: res', res);
        this.changePassword = res.msg;
      },
      (err) => {
        //console.log('changePassword: error', err);
        this.changePassword = err['msg'];
      }
    );
  }

  set_API_server(): void {
    console.log('set_API_server:', this.my_api_server);
    this.adcService.set_API_server_origin(this.my_api_server);
  }

  doLogout(): void {
    //console.log('doLogout:');
    this.adcService.logoutADCservice()
    .subscribe((res: ResLogout) => {
      //console.log('doLogout: res', res);
      this.logout = res.msg;
      this.appComponent.ngOnInit();  // Adminメニューを表示するかしないか、反映
      this.adcService.update_status_bar();
    });
  }
}
