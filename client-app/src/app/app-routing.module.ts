import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { FileCheckerComponent } from './file-checker/file-checker.component';

const routes: Routes = [
  { path: 'file-checker', component: FileCheckerComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {useHash: true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
