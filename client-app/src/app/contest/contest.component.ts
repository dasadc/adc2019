import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
import { QNumberList, ANumberList } from '../apiresponse';

@Component({
  selector: 'app-contest',
  templateUrl: './contest.component.html',
  styleUrls: ['./contest.component.css']
})
export class ContestComponent implements OnInit {
  aNumber: number = 1;
  qNumberList: QNumberList;
  qText: string;
  qFilename: string;
  uploadResults: string;
  aNumberList: ANumberList;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.getQNumberList();
  }

  getQNumberList() {
    //let username: string = this.adcService.getUsername();
    this.adcService.getQNumberList()
      .subscribe(res => {
        //console.log('getQNumberList: res=', res);
        this.qNumberList = res;
        //this.myQList = res.entries;
      });
  }

  getANumberList() {
    let username: string = this.adcService.getUsername();
    this.adcService.getANumberList(username)
      .subscribe(res => {
        console.log('getANumberList: res=', res);
        this.aNumberList = res;
      });
  }

  viewQFile(i: number) {
    //console.log('viewQFile', i);
    this.adcService.getQ(i)
      .subscribe(res => {
          //console.log(res);
          this.qFilename = `Q${i}.txt`;
          this.qText = res['text'];
      })
  }

  downloadQFile(i: number) {
    let username: string = this.adcService.getUsername();
    let filename: string = `Q${i}.txt`;
    this.adcService.getQ(i)
      .subscribe(res => {
          this.adcService.downloadFile(res['text'], 'text/plain', filename);
      })
  }

  /** adccli put-a相当の処理を行う */
  putAFile(f: Object) {
    console.log('putAFile', this.aNumber);
    console.log('filename', f['filename']);
    console.log('text', f['text']);
    if (f['filename'] === void 0 || f['text'] === void 0) {
      return;
    }
    let username: string = this.adcService.getUsername();
    this.adcService.putA(username, this.aNumber, f['text'], f['filename'])
      .subscribe(
        (res: string) => {
        console.log('res=', res);
        this.uploadResults = res;
        //this.getUserAList();
      },
      (res: string) => {
        console.log('ERROR', res);
        this.uploadResults = res;
      });
  }


  onCleared(c: boolean) {
    console.log('contest: onCleared', c)
  }

}
