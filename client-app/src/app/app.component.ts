import { Component } from '@angular/core';
import { Title } from '@angular/platform-browser';

import { AdcService } from './adc.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  info: Object ;
  title: string ;
  url_help: string;
  iamAdmin: boolean;

  constructor(private adcService: AdcService,
              private titleService: Title) {
    this.url_help = 'https://github.com/dasadc/';
  }

  ngOnInit() {
    this.adcService.system_info()
      .subscribe((info: Object) => {
        this.info = info;
        this.url_help = info['url']['client-app']['README'];
        //console.log('system_info', info['url']['client-app']['README'])
      },
      (err) => {
        console.log('ERROR: app.component: system_info:', err);
      });
    this.adcService.version()
      .subscribe((ver: number) => {
        this.title = `DAS${ver} Algorithm Design Contest (ADC${ver})`;
      });
    this.titleService.setTitle(this.title);  // Webブラウザに表示されるタイトルを設定する

    this.adcService.iamadmin()
      .subscribe(res => {
        this.iamAdmin = res;
        //this.check();
      },
      (err) => {
        this.iamAdmin = false;
        //console.log('app.component: err=', err);
      });
  }

  check() {
    console.log('Check now', this.iamAdmin);
  }
}
