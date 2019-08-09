import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
//import { MessageService } from '../message.service';

@Component({
  selector: 'app-file-view',
  templateUrl: './file-view.component.html',
  styleUrls: ['./file-view.component.css']
})
export class FileViewComponent implements OnInit {

  constructor(public adcService: AdcService) { }
  //constructor(private adcService: AdcService) { }
  //constructor(private messageService: MessageService) { }

  ngOnInit() {
  }
}
