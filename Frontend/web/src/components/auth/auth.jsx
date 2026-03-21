import React, { use, useEffect, useState } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import { useBodyClass } from '../../hooks/useBody'
import { useAuth } from '../../hooks/useAuth'
import '../index.css'
import './auth.css'

//------------Main:

export function Log_form({ log, onClose }) {
  if (!log) return 
  return (
    <div className='log-form'>
      <div className='poster-log'><i className="fa-solid fa-triangle-exclamation"></i></div>
      <h1>{log}</h1>
      <button
       className='back-log' 
       onClick={onClose}
      ><i className="fa-regular fa-circle-xmark"></i></button>
    </div>
  )
}

export function MainWindow({ children, log, onClose }){
  const nav = useNavigate()
  useBodyClass('auth-bg')

  return (
    <>
      <div className='controls'>
         <div className='auth-window'>
           <div className='auth-section'>
             {children}
           </div>
           <button
            className='back-btn'
            onClick={() => nav(-1)}
           >Back</button>
         </div>
         <Log_form log={log} onClose={onClose} />
      </div> 
    </>    
  )
}

//------------Register:

export function Reg_login() {

  const [username, setUsername] = useState('')
  const nav = useNavigate()

  const NextClick = () => {
    if (username.trim()) {
      nav(`/a/reg/${username}`)
    }
  }
  return (
    <>
       <div className='icon-auth'><i className="fa-solid fa-pen-nib"></i></div>
      <div className='auth-input'>
         <form>
           <p>Create unique username</p>
           <div className='input-wrapper'>
            <span><i className="fa-solid fa-at"></i></span>
           <input
           type='text'
           placeholder='Enter Username'
           value={username}
           onChange={(e) => {
            setUsername(e.target.value)
           }}
           required></input>
           </div>
           <button onClick={NextClick}>Next</button>
         </form>
      </div>
    </>
  )
}

export function Reg_password({ onLog }) {
  const [isPass, setIsPass] = useState(false)
  const [password, setPassword] = useState('')
  const { username } = useParams()

  const nav = useNavigate()

  const { load, register } = useAuth()
  const handleReg = async () => {
    if(!password || password.length < 8 || password.length > 100) {
      onLog('Incorrect password, try again')
      return
    }

    const res = await register(username, password)
    if(!res) {
       onLog('Error')
    }
  }

  return (
    <>
       <div className='icon-auth'><i className="fa-solid fa-lock"></i></div>
      <div className='auth-input'>
         <form>
           <p>Create safe password for <b>@{username}</b></p>
           <div className='input-wrapper'>
             <span
              onClick={() => setIsPass(!isPass)}
              style={{cursor: 'pointer', fontSize: '20px', opacity: '1'}}
             ><i className={`fa-regular ${ isPass ? 'fa-eye' : 'fa-eye-slash' }`}></i></span>
             <input
              type={isPass ? 'text' : 'password'}
              value={password}
              onChange={(e) => {
                 setPassword(e.target.value)
              }}
              placeholder='Enter Password'
              required></input>
           </div>
           <button type="button" onClick={handleReg}>Next</button>
         </form>
      </div>
    </>
  )
}

//------------Login:

export function Login_login() {

  const [username, setUsername] = useState('')
  const nav = useNavigate()

  const NextClick = () => {
    if (username.trim()) {
      nav(`/a/login/${username}`)
    }
  }
  return (
    <>
       <div className='icon-auth'><i className="fa-regular fa-star"></i></div>
      <div className='auth-input'>
         <form>
           <p>Enter your username</p>
           <div className='input-wrapper'>
            <span><i className="fa-solid fa-at"></i></span>
           <input
           type='text'
           placeholder='Enter Username'
           value={username}
           onChange={(e) => {
            setUsername(e.target.value.trim())
           }}
           required></input>
           </div>
           <button onClick={NextClick}>Next</button>
         </form>
      </div>
    </>
  )
}

export function Login_password() {
  const [isPass, setIsPass] = useState(false)
  const nav = useNavigate()
  const {username} = useParams()
  
  return (
    <>
       <div className='icon-auth'><i className="fa-solid fa-key"></i></div>
      <div className='auth-input'>
         <form>
           <p>Enter password from <b>@{username}</b></p>
           <div className='input-wrapper'>
             <span
              onClick={() => setIsPass(!isPass)}
              style={{cursor: 'pointer', fontSize: '20px', opacity: '1'}}
             ><i className={`fa-regular ${ isPass ? 'fa-eye' : 'fa-eye-slash' }`}></i></span>
             <input
              type={isPass ? 'text' : 'password'} placeholder='Enter Password'
             ></input>
           </div>
           <button>Next</button>
         </form>
      </div>
    </>
  )
}