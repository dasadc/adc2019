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
  enabledDescrTbl = {
    0: 'manual state transition',
    1: 'automatic state transition, depending on current time'
  };
  stateDescription: string;
  stateDescrTbl = {
    'init': 'initial',
    'im0': 'intermission (0)',
    'Qup': 'You can upload Q data.',
    'im1': 'intermission (1)',
    'Aup': 'You can upload A data.',
    'im2': 'intermission (2)',
  }

  constructor(private adcService: AdcService) { }

  ngOnInit() {
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
        if (s % 5 == 0) { // きっとうまい方法があるはず
          this.updateUsername();
        }
      });
  }

  updateUsername(): void { // なんか変な処理
    //console.log('updateUserName (A)')
    if (this.username === void 0) {
      this.usernameDescription = 'Please login';
      this.adcService.whoami()
        .subscribe((res: ResMsgOnly) => {
          this.username = res.msg;
        });
        //console.log('updateUserName (B)')
    }
    if (this.authenticated === void 0 || !this.authenticated) {
      let token: string = this.adcService.getAccessToken();
      if (token === void 0) {
        this.authenticated = false;
        this.usernameDescription = 'not authenticated. Please login';
      } else {
        this.authenticated = true;
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
        this.stateDescription = this.stateDescrTbl[tk['state']]
        this.enabledDescription = this.enabledDescrTbl[tk['enabled']]
      });
  }
}
