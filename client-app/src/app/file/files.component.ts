import { Component, OnInit, EventEmitter, Output, Input } from '@angular/core';
import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-files',
  templateUrl: './files.component.html',
  styleUrls: ['./file.component.css']
})
export class FilesComponent implements OnInit {
  text: string;
  filename: string;
  @Input() accept_file_type: string;
  @Output() cleared = new EventEmitter<boolean>();

  public files: NgxFileDropEntry[] = [];
  public list_of_files: Object[] = [];
  //@Output() list_of_files = EventEmitter<Object[]>();
  public qnum: number = 0;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

  public dropped(files: NgxFileDropEntry[]) {
    this.files = files;
    for (const droppedFile of files) {
      //console.log('droppedFile=', droppedFile);
      // Is it a file?
      if (droppedFile.fileEntry.isFile) {
        const fileEntry = droppedFile.fileEntry as FileSystemFileEntry;
        //console.log('fileEntry=', fileEntry);
        fileEntry.file((file: File) => {
          // Here you can access the real file
          //console.log('file?', droppedFile.relativePath, file);
          this.qnum += 1;
          let tmp = {qnum: this.qnum,
                     filename: file.name,
                     size: file.size,
                     file: file};
          this.list_of_files.push(tmp);
          //console.log(tmp);
          /*
      	  this.filename = file.name;
      	  this.adcService.readFile3(file)
  	         .subscribe(txt => this.text = txt);
          */
	      });
      } else {
        // It was a directory (empty directories are added, otherwise only files)
        const fileEntry = droppedFile.fileEntry as FileSystemDirectoryEntry;
        //console.log('dir?', droppedFile.relativePath, fileEntry);
      }
    }
  }

  /*
  public fileOver(event){
    console.log('files: fileOver()', event);
  }

  public fileLeave(event){
    console.log('files: fileLeave()', event);
  }
  */

  onchangeFile(files: FileList) {
    console.log('files: onchangeFile()', files);
    for ( let i = 0; i < files.length; i ++ ) {
      this.qnum += 1;
      let tmp = {qnum: this.qnum,
                 filename: files[i].name,
                 size: files[i].size,
                 file: files[i]};
      this.list_of_files.push(tmp);
      /*
      this.filename = files[i].name;
      this.adcService.readFile3(files[i])
	     .subscribe(txt => this.text = txt);
      */
    }
  }

  clear_data() {
    //console.log('files: clear_data()');
    this.files = [];
    this.list_of_files = [];
    this.text = undefined;
    this.filename = undefined;
    this.adcService.clearText3();
    this.cleared.emit(true);
  }

  view_file(n: number) {
    n -= 1;  // n = 1, 2, 3, ... の値をとるので
    console.log('view_file', n, this.list_of_files[n]['file']);
    this.filename = this.list_of_files[n]['filename'];
    this.adcService.readFile3(this.list_of_files[n]['file'] as File)
     .subscribe(txt => this.text = txt);
  }

  cut_file(n: number) {
    console.log('cut_file', n);
    let tmp_list_of_files: Object[] = [];
    let tmp_qnum: number = 0;
    for (let i=0; i<this.list_of_files.length; i++) {
      if (this.list_of_files[i]['qnum'] == n) {
        //cut
      } else {
        tmp_qnum += 1;
        let tmp = {qnum: tmp_qnum,
                   filename: this.list_of_files[i]['filename'],
                   size: this.list_of_files[i]['size'],
                   file: this.list_of_files[i]['file']};
        tmp_list_of_files.push(tmp);
      }
    }
    this.list_of_files = tmp_list_of_files;
    this.qnum = tmp_qnum;
  }
}
