import { Component, OnInit, Input } from '@angular/core';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file-view',
  templateUrl: './file-view.component.html',
  styleUrls: ['./file-view.component.css']
})
export class FileViewComponent implements OnInit {
  @Input() text: string;
  @Input() filename: string;
  
  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }
}
