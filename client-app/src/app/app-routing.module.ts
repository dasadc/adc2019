import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { FileCheckerComponent } from './file-checker/file-checker.component';
import { LoginComponent } from './login/login.component';
import { MyAccountComponent } from './my-account/my-account.component';

const routes: Routes = [
  { path: 'file-checker', component: FileCheckerComponent },
  { path: 'login', component: LoginComponent },
  { path: 'my-account', component: MyAccountComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {useHash: true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
