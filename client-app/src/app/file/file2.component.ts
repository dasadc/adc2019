import { Component, OnInit } from '@angular/core';
import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file2',
  templateUrl: './file2.component.html',
  styleUrls: ['./file.component.css']
})
export class FileComponent2 implements OnInit {

  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

  public files: NgxFileDropEntry[] = [];
  
  public dropped(files: NgxFileDropEntry[]) {
    this.files = files;
    for (const droppedFile of files) {
      // Is it a file?
      if (droppedFile.fileEntry.isFile) {
        const fileEntry = droppedFile.fileEntry as FileSystemFileEntry;
        fileEntry.file((file: File) => {
          // Here you can access the real file
	  this.adcService.readFile2(file);
        });
      }
    }
  }
  
  onchangeFile(files: any) {
    for ( let i = 0; i < files.length; i ++ ) {
      this.adcService.readFile2(files[i]);
    }
  }
}
