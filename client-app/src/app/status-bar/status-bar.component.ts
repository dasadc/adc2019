import { Component, OnInit, Input } from '@angular/core';
import { Observable, interval } from 'rxjs';

import { AdcService } from '../adc.service';
import { ResMsgOnly, ResTimekeeper } from '../apiresponse';

@Component({
  selector: 'app-status-bar',
  templateUrl: './status-bar.component.html',
  styleUrls: ['./status-bar.component.css']
})
export class StatusBarComponent implements OnInit {
  datetime: Date;
  clk: ResTimekeeper;
  authenticated: boolean;
  username: string;
  usernameDescription: string;
  enabledDescription: string;
  stateDescription: string;
  roundDescription: string;
  updateUsername_error_count: number = 0;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.adcService.set_status_bar_component(this);
    this.updateUsername();
    this.getTimekeeper();
    const secondsCounter = interval(1000)
      .subscribe(n => {
        this.datetime = new Date();
        //console.log(`It's been ${n} seconds since subscribing!`);
        let m: number = this.datetime.getMinutes();
        let s: number = this.datetime.getSeconds();
        if (s == 0 &&
            (m==0 || m==3 || m==15 || m==20 || m==55)) {
          this.getTimekeeper();
        }
        if (s % 10 == 0) { // きっとうまい方法があるはず
          this.updateUsername();
        }
      });
  }

  updateStatus() { // update statusボタンをクリック。status-barを再描画させたい
    this.updateUsername();
    this.getTimekeeper();
  }
  
  updateUsername(): void { // なんか変な処理
    /*
    // Do not call API here !!!
    //console.log('updateUserName', 'username', this.username, 'authenticated', this.authenticated)
    if (this.username === void 0) {
      this.username = this.adcService.getUsernameCurrent()
    }
    if (this.authenticated === void 0 || !this.authenticated) {
      let token: string = this.adcService.getAccessTokenCurrent();
      if (token === void 0) {
        this.authenticated = false;
        this.usernameDescription = 'not authenticated. Please login';
      } else {
        this.authenticated = true;
        this.usernameDescription = 'authenticated';
      }
    }
    */

    //console.log('updateUserName (A)', this.updateUsername_error_count, 'username', this.username, 'authenticated', this.authenticated)
    if (5 < this.updateUsername_error_count) {
      return;
    }
    this.updateUsername_error_count ++;
    if (this.username === void 0) {
      this.usernameDescription = 'Please login';
      this.adcService.whoami()
        .subscribe(
          (res: ResMsgOnly) => {
          this.username = res.msg;
        },
        (err) => {
          console.log('updateUserName (C)', err['message']);
        }
      );
      //console.log('updateUserName (B)')
    }
    if (this.authenticated === void 0 || !this.authenticated) {
      let token: string = this.adcService.getAccessToken();
      if (token === void 0) {
        this.authenticated = false;
        this.usernameDescription = 'not authenticated. Please login';
      } else {
        this.authenticated = true;
        //console.log('token=', token)
        this.usernameDescription = 'authenticated';
      }
      //console.log('updateUserName (C)')
    }
    let u = this.adcService.getUsername();
    if (u != this.username) {
      this.authenticated = false;
      this.username = this.adcService.getUsername();
    }

  }

  getTimekeeper() {
    this.adcService.getTimekeeper()
      .subscribe(tk => {
        //console.log('status-bar: tk=', tk);
        this.clk = tk;
        this.roundDescription = ResTimekeeper.roundDescrTbl[tk['round']]
        this.stateDescription = ResTimekeeper.stateDescrTbl[tk['state']]
        this.enabledDescription = ResTimekeeper.enabledDescrTbl[tk['enabled']]
      });
  }
}
