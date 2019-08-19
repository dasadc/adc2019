import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file2',
  templateUrl: './file2.component.html',
  styleUrls: ['./file.component.css']
})
export class FileComponent2 implements OnInit {
  text: string;
  filename: string;
  @Output() cleared = new EventEmitter<boolean>();

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
	  this.filename = file.name;
	  this.adcService.readFile2(file)
	    .subscribe(txt => this.text = txt);
        });
      }
    }
  }
  
  onchangeFile(files: FileList) {
    for ( let i = 0; i < files.length; i ++ ) {
      this.filename = files[i].name;
      this.adcService.readFile2(files[i])
	.subscribe(txt => this.text = txt);
    }
  }

  clear_data() {
    this.text = undefined;
    this.filename = undefined;
    this.adcService.clearText2();
    this.cleared.emit(true);
  }
}
