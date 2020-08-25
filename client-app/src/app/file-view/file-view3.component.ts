import { Component, OnInit, Input } from '@angular/core';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file-view3',
  templateUrl: './file-view3.component.html',
  styleUrls: ['./file-view.component.css']
})
export class FileViewComponent3 implements OnInit {
  @Input() text: string;
  @Input() filename: string;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }
}
