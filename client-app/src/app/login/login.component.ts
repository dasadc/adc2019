import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
import { ResLogin, ResLogout } from '../apiresponse';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  username: string;
  password: string;
  loginMessage: string;
  access_token: string;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.username = this.adcService.getUsername();
    this.access_token = this.adcService.getAccessToken();
  }

  doLogin(): void {
    //console.log('doLogin: username='+this.username+'  password='+this.password);
    this.adcService.loginADCservice(this.access_token, this.username, this.password)
    .subscribe((res: ResLogin) => {
      //console.log('doLogin: res', res);
      this.loginMessage = res.msg;
      this.access_token = res.token;
    });
  }

  doLogout(): void {
    //console.log('doLogout:');
    this.adcService.logoutADCservice()
    .subscribe((res: ResLogout) => {
      //console.log('doLogout: res', res);
      this.loginMessage = res.msg;
      this.access_token = undefined;
    });
  }
}
