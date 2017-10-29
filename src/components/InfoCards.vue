<template>
   <v-layout
     column
     wrap
     class="my-5"
     align-center
   >
     <v-flex xs12>
       <v-container grid-list-xl>
         <v-layout row wrap align-center>
           <v-flex xs12 md4>
             <v-card class="elevation-0 transparent">
               <v-card-text class="text-xs-center">
                 <v-icon x-large class="blue--text text--lighten-2">color_lens</v-icon>
               </v-card-text>
               <v-card-title primary-title class="layout justify-center">
                 <div class="headline text-xs-center">Intuitive UI</div>
               </v-card-title>
               <v-card-text>
                 Extensive keyboard shortcuts and smart editing tools designed for speed
                 provide unparalleled speed and control of your workflow.
               </v-card-text>
             </v-card>
           </v-flex>
           <v-flex xs12 md4>
             <v-card class="elevation-0 transparent">
               <v-card-text class="text-xs-center">
                 <v-icon x-large class="blue--text text--lighten-2">flash_on</v-icon>
               </v-card-text>
               <v-card-title primary-title class="layout justify-center">
                 <div class="headline">AI Acceleration</div>
               </v-card-title>
               <v-card-text>
                 Cras facilisis mi vitae nunc lobortis pharetra. Nulla volutpat tincidunt ornare.
                 Pellentesque habitant morbi tristique senectus.
               </v-card-text>
             </v-card>
           </v-flex>
           <v-flex xs12 md4>
             <v-card class="elevation-0 transparent">
               <v-card-text class="text-xs-center">
                 <v-icon x-large class="blue--text text--lighten-2">build</v-icon>
               </v-card-text>
               <v-card-title primary-title class="layout justify-center">
                 <div class="headline text-xs-center">Open Source</div>
               </v-card-title>
               <v-card-text>
                 Download and run a basic version of our app for free locally on your machine!
               </v-card-text>
             </v-card>
           </v-flex>
         </v-layout>
       </v-container>
     </v-flex>
   </v-layout>

</template>


<script type = "text/javascript" >

export default {
}
