import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
import { UserQEntry, ResUserQList } from '../apiresponse';

@Component({
  selector: 'app-upload-q',
  templateUrl: './upload-q.component.html',
  styleUrls: ['./upload-q.component.css']
})
export class UploadQComponent implements OnInit {
myQList: UserQEntry[];
myQText: string;
myQFilename: string;
myQNumber: number[] = [1, 2, 3];
postQNumber: number = 1;
uploadResults: string;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.getUserQList();
  }

  getUserQList() {
    let username: string = this.adcService.getUsername();
    this.adcService.getUserQList(username)
      .subscribe(res => {
        //console.log('getUserQList: res=', res);
        this.myQList = res.entries;
      });
  }

  viewQFile(i: number, filename: string) {
    //console.log('viewQFile', i, filename);
    let username: string = this.adcService.getUsername();
    this.adcService.getUserQ(username, i)
      .subscribe(res => {
          //console.log(res);
          this.myQFilename = filename;
          this.myQText = res;
      })
  }

  deleteQFile(i: number) {
    //console.log('deleteQFile', i);
    let username: string = this.adcService.getUsername();
    this.adcService.deleteUserQ(username, i)
      .subscribe(res => {
        console.log('res=', res);
        this.getUserQList();
      })
  }

  postQFile(f: Object) {
    //console.log('postQFile', this.postQNumber);
    //console.log('filename', f['filename']);
    //console.log('text', f['text']);
    if (f['filename'] === void 0 || f['text'] === void 0) {
      return;
    }
    let username: string = this.adcService.getUsername();
    this.adcService.postUserQ(username, this.postQNumber, f['text'], f['filename'])
      .subscribe(
        (res: string) => {
        //console.log('res=', res);
        this.uploadResults = res;
        this.getUserQList();
      },
      (res: string) => {
        //console.log('ERROR', res);
        this.uploadResults = res;
      });
  }

  onCleared(c: boolean) {
    //console.log('upload-q onCleared', c)
  }
}
