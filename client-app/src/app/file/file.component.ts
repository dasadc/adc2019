import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file',
  templateUrl: './file.component.html',
  styleUrls: ['./file.component.css']
})
export class FileComponent implements OnInit {
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
      //console.log(droppedFile)
      // Is it a file?
      if (droppedFile.fileEntry.isFile) {
        const fileEntry = droppedFile.fileEntry as FileSystemFileEntry;
        fileEntry.file((file: File) => {

          // Here you can access the real file
          //console.log('file?', droppedFile.relativePath, file);
	        this.filename = file.name;
	        this.adcService.readFile1(file)
	         .subscribe(txt => this.text = txt);

          /**
           // You could upload it like this:
           const formData = new FormData()
           formData.append('logo', file, relativePath)

           // Headers
           const headers = new HttpHeaders({
           'security-token': 'mytoken'
           })

           this.http.post('https://mybackend.com/api/upload/sanitize-and-save-logo', formData, { headers: headers, responseType: 'blob' })
           .subscribe(data => {
           // Sanitized logo returned from backend
           })
          **/

        });
      } else {
        // It was a directory (empty directories are added, otherwise only files)
        const fileEntry = droppedFile.fileEntry as FileSystemDirectoryEntry;
        //console.log('dir?', droppedFile.relativePath, fileEntry);
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
      this.adcService.readFile1(files[i])
	.subscribe(txt => this.text = txt);

      /*
      let file = files[i];
      let reader = new FileReader(); // https://developer.mozilla.org/ja/docs/Web/API/FileReader
      reader.onload = (e) => {
	this.file_contents = reader.result;
      }
      //console.log('file', file);
      reader.readAsText(file);
      */
    }
  }

  /*
  public openFileSelector() {
    console.log('openFileSelector')
  }
  */

  /*
  public getText(): string {
    return this.text;
  }
  */

  clear_data() {
    //console.log('file: clear_data()');
    this.text = undefined;
    this.filename = undefined;
    this.adcService.clearText1();
    this.cleared.emit(true);
  }
}
