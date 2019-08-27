import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
import { ResTimekeeper, AdminQList } from '../apiresponse';

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
  adminQAll: Object;
  adminAAll: Object;


  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.getTimekeeper();
    this.getTestMode();
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
}
