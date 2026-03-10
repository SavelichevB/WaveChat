import React, { useState } from 'react'
import { Header, MainWindow, DownloadWindow, Footer } from '../components/main/main.jsx'

export function E404() {
    return (
        <>
        <Header/>
        <div
         style={{display: 'flex', justifySelf: 'center', marginTop: '100px'}}
        >
            <h1>Page not found</h1>
            <h3 style={{color: 'orange', marginLeft: '2px'}}>404 - Not Found</h3>
            <h1 style={{fontSize: '100px', transform: 'rotate(25deg)', left: '10%'}}>:(</h1>
        </div>
        <Footer/>
        </>
    )
}

export function MainPage() {
    return (
        <>
         <Header activePoint="main"/>
         <MainWindow/>
         <Footer/>
        </>
    )
}

export function DowPage() {
    return (
        <>
        <Header activePoint="dow"/>
        <DownloadWindow/>
        <Footer/>
        </>
    )
}