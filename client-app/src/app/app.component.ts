import { Component } from '@angular/core';
import { Title } from '@angular/platform-browser';

import { AdcService } from './adc.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title: string ;

  constructor(private adcService: AdcService,
              private titleService: Title) { }

  ngOnInit() {
    this.adcService.version()
      .subscribe((ver: number) => {
        this.title = `DAS${ver} Algorithm Design Contest (ADC${ver})`;
      });
    this.titleService.setTitle(this.title);  // Webブラウザに表示されるタイトルを設定する
  }

  check() {
    console.log('Check now');
  }
}
