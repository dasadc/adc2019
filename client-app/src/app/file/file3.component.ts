import { Component, OnInit, EventEmitter, Output, Input } from '@angular/core';
import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file3',
  templateUrl: './file3.component.html',
  styleUrls: ['./file.component.css']
})
export class FileComponent3 implements OnInit {
  text: string;
  filename: string;
  @Input() accept_file_type: string;
  @Output() cleared = new EventEmitter<boolean>();

  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

  public files: NgxFileDropEntry[] = [];

  public dropped(files: NgxFileDropEntry[]) {
    this.files = files;
    for (const droppedFile of files) {
      //console.log(droppedFile)
      // Is it a file?
      if (droppedFile.fileEntry.isFile) {
        const fileEntry = droppedFile.fileEntry as FileSystemFileEntry;
        fileEntry.file((file: File) => {
          // Here you can access the real file
          //console.log(droppedFile.relativePath, file);
      	  this.filename = file.name;
      	  this.adcService.readFile3(file)
  	         .subscribe(txt => this.text = txt);
	      });
      } else {
        // It was a directory (empty directories are added, otherwise only files)
        const fileEntry = droppedFile.fileEntry as FileSystemDirectoryEntry;
        //console.log(droppedFile.relativePath, fileEntry);
      }
    }
  }

  public fileOver(event){
    //console.log(event);
  }

  public fileLeave(event){
    //console.log(event);
  }

  onchangeFile(files: FileList) {
    //console.log('files', files);
    for ( let i = 0; i < files.length; i ++ ) {
      this.filename = files[i].name;
      this.adcService.readFile3(files[i])
	     .subscribe(txt => this.text = txt);
    }
  }

  clear_data() {
    //console.log('file: clear_data()');
    this.text = undefined;
    this.filename = undefined;
    this.adcService.clearText3();
    this.cleared.emit(true);
  }
}
