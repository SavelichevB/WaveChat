import React, { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import './main.css' 
import '../index.css'

  export function Header({ activePoint }) {
    const nav = useNavigate()
    return (
      <>
        <div className="up-blc">
            <div className="up-btn">
                <label style={{
                    borderBottom: activePoint === 'main' ?  '3px solid var(--hover-effect)' : ''
                }}
                onClick={() => nav('/')}
                >
                    <a>Main</a>
                </label>
                <label style={{
                   borderBottom: activePoint === 'dow' ?  '3px solid var(--hover-effect)' : ''                   
                }}
                onClick={() => nav('/dow')}
                >
                    <a>Download</a>
                </label>
                <label style={{
                   borderBottom: activePoint === 'api' ?  '3px solid var(--hover-effect)' : ''   
                }}
                onClick={() => nav('/api')}
                >
                    <a>API</a>
                </label>
            </div>
            <div className="up-link">WaveChat</div>
        </div>  
      </> 
    )
  }

  export function Footer() {
    return (
     <>
     <div className='footer'>
         <div className='f-logo'></div>
         <div className='f-block1'>
            <h4>ch.wavemini.ru</h4>
            <p>© {new Date().getFullYear()} WaveChat. Все права защищены.</p>
         </div>
         <div className='f-block2'>
            <i className="fa-brands fa-telegram"></i>
            <i className="fa-brands fa-tiktok"></i> 
            <i className="fa-solid fa-link"></i>
         </div>
     </div>
     </>
   )
  }

  export function MainWindow() {
    const nav = useNavigate()
    return (
     <div className='controls'>
     <div className="info-menu">
        <div className="home-block">
            <div className="logo"></div>
            <section>Welcome to WaveChat</section>
            <div className="login-block">
                <label>
                    <button
                     onClick={() => nav('/a/login')}
                    >Login</button>
                </label>
                <label>
                    <button
                     onClick={() => nav('/a/reg')}
                    >Registration</button>
                </label>
            </div>
        </div>
     </div>     
     </div>
    )
  }

  export function DownloadWindow() {
    return (
        <div className='controls'>
         <div className='dowl-menu'>
            <div className='dowl-block'>
                <section>Use WaveChat now:</section>
                <div className='dowl-section'>
                    <label>
                        <div className='dowl-img' style={{ backgroundImage: `url(https://wavemini.ru/a/wavechat/windows.png)`}}></div>
                        <button>Download for Windows</button>
                    </label>
                    <label>
                        <div className='dowl-img' style={{ backgroundImage: `url(https://wavemini.ru/a/wavechat/android.png)`}}></div>
                        <button>Download for Android</button>
                    </label>
                    <label>
                        <div className='dowl-img' style={{ backgroundImage: `url(https://wavemini.ru/a/wavechat/web.png)`}}></div>
                        <button>Сontinue for Web</button>
                    </label>
                </div>
            </div>          
         </div>
        </div>
    )
  }

