import { Component, OnInit, AfterViewInit, ViewChild } from '@angular/core';
//import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';
import { readFile } from '../rx-file-reader';
import { Observable, of, from } from 'rxjs';
import { catchError, map, tap, flatMap, reduce } from 'rxjs/operators';

import { AdcService } from '../adc.service';
import { UserQEntry, ResUserQList, ResMsgOnly } from '../apiresponse';

import { FilesComponent } from '../file/files.component';

@Component({
  selector: 'app-upload-q',
  templateUrl: './upload-q.component.html',
  styleUrls: ['./upload-q.component.css']
})
export class UploadQComponent implements OnInit, AfterViewInit {
  myQList: UserQEntry[];
  myQText: string;
  myQFilename: string;
  myQNumber: number[] = [1, 2, 3];
  postQNumber: number = 1;
  uploadResults: string;

  @ViewChild(FilesComponent)
  private filesComponent: FilesComponent;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
    //this.getUserQList();  // 希望通りには動作しない

    /*
    from([1,2,3,4])
      .pipe(
        map(n => n * 2),
        map(m => m + 1)
      )
      .subscribe(x => console.log('(map)', x));
      // 3, 5, 7, 9
    */

    /*
    from([1,2,3,4])
    .pipe(
      flatMap(n => {
        console.log('fm0', n);
        return of(n * 2);
      }),
      flatMap(m => {
        console.log('fm1', m);
        return of(m + 1);
      })
    )
    .subscribe(x => console.log('(flatMap)', x));
    */
    /*
    from([1,2,3,4])
    .pipe(
      flatMap((n: number) => {
        console.log('fm0', n);
        return of([n * 2, n]);
      }),
      flatMap((m: number[]) => {
        console.log('fm1', m);
        m.unshift(m[0] + 1)
        return of(m);
      })
    )
    .subscribe((x: number[]) => console.log('(flatMap)', x));
    */
    /*
    fm0 1
    fm1 Array [ 2, 1 ]
    (flatMap) Array(3) [ 3, 2, 1 ]

    fm0 2
    fm1 Array [ 4, 2 ]
    (flatMap) Array(3) [ 5, 4, 2 ]

    fm0 3
    fm1 Array [ 6, 3 ]
    (flatMap) Array(3) [ 7, 6, 3 ]

    fm0 4
    fm1 Array [ 8, 4 ]
    (flatMap) Array(3) [ 9, 8, 4 ]
    */

    /*
    from([1,2,3,4])
    .pipe(
      reduce((acc: number, curr: number) => {
        console.log('acc=', acc, ' curr=', curr);
        return acc + curr;
      }, 10)
    )
    .subscribe((x: number) => console.log('(reduce)', x));
    */
    /*
    acc= 10  curr= 1
    acc= 11  curr= 2
    acc= 13  curr= 3
    acc= 16  curr= 4
    (reduce) 20
    */
  }

  ngAfterViewInit() {
    this.getUserQList();
  }

  getUserQList() {
    //let username: string = this.adcService.getUsername();
    this.adcService.whoami()
      .subscribe((res: ResMsgOnly) => {
        let username: string = res.msg;
        this.adcService.getUserQList(username)
          .subscribe(res => {
            //console.log('getUserQList: res=', res);
            if (res !== void 0) {
              this.myQList = res.entries;
              //console.log('upload-q: myQList', this.myQList);
            }
          });
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

  downloadQFile(i: number, filename: string) {
    let username: string = this.adcService.getUsername();
    this.adcService.getUserQ(username, i)
      .subscribe(res => {
          this.adcService.downloadFile(res, 'text/plain', filename);
      })
  }

  deleteQFile(i: number) {
    //console.log('deleteQFile', i);
    let username: string = this.adcService.getUsername();
    this.adcService.deleteUserQ(username, i)
      .subscribe(res => {
        console.log('res=', res);      flatMap((m: number[]) => {
        console.log('fm1', m);
        m.unshift(m[0] + 1)
        return of(m);
      })

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

  startUploadQFiles_localvariable(a: Object) {
    console.log('startUploadQFiles_localvariable', a['list_of_files']);
  }

  startUploadQFiles() {
    //console.log('startUploadQFiles', this.filesComponent);
    let list_of_files: Object[] = this.filesComponent.list_of_files;
    //let files: NgxFileDropEntry[] = this.filesComponent.files;
    let username: string = this.adcService.getUsername();
    this.uploadResults = '';
    for (const f of list_of_files) {
      let file: File = f['file'];
      console.log(file);
      readFile(file)
        .subscribe(
          (txt: string) => {
            //console.log(`Q${f['qnum']}\n${f['filename']}\n${file.name}\n${txt}`);
            this.adcService.postUserQ(username, f['qnum'], txt, f['filename'])
              .subscribe( // ネスティングしてるのが汚い。pipe? flatmap?
                (res: string) => {
                //console.log('res=', res);
                this.uploadResults += res + '\n';
              },
              (res: string) => {
                //console.log('ERROR', res);
                this.uploadResults += res + '\n';
              },
              () => {
                console.log('completed');
                this.getUserQList();
                this.filesComponent.clear_data();
              });
          });
      }
      /*
      let qnum: number = 0;
      let filename: string = '';
      from(list_of_files)
        .pipe(
          flatMap((x: Object) => {
            let file: File = x['file'];
            qnum = x['qnum'];
            filename = file.name;
            //let xx: Observable<string> = readFile(file);
            console.log('pipe0', file);
            return readFile(file);
          }),
          flatMap((txt: string) => {
            console.log('pipe1', qnum, filename, txt);
            return this.adcService.postUserQ(username, qnum, txt, filename);
          })
        )
        .subscribe(
          (res) => {
            console.log('res', res);
          },
          (err) => {
            console.log('ERROR', err);
          },
          () => {
            console.log('completed.')
          }
        );
      */
  }

  onCleared(c: boolean) {
    //console.log('upload-q onCleared', c)
  }
}
