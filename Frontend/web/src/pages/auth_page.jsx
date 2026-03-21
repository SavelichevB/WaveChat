import React, { use, useState } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import {MainWindow, Reg_login, Reg_password, Login_login, Login_password} from '../components/auth/auth'

export function RegistePage() {
  const { username } = useParams()
  const { logs, setlogs } = useParams()
  const [ isLog, setIsLog ] = useState(true)
  const [ childLog, setClildLog] = useState('')


  const isValid = username && username.length >= 3 && username.length <= 30
  const validUsername = isValid ? username : ''
  const logMessage = username && !isValid ? 'Incorrect username' : ''

  const handleChild = (message) => {
    setClildLog(message)
  }
  const handleClose = () => {
    setIsLog(false),
    setClildLog('')
  }

  const displayLog = childLog || (isLog ? logMessage : '')

  return (
     <MainWindow
      log={displayLog}
     onClose={handleClose}
     >
       {validUsername ? <Reg_password onLog={handleChild}/> : <Reg_login/>}
    </MainWindow>
  )
}

export function LoginPage() {
  const { username } = useParams()
  const { logs, setlogs } = useParams()
  const [ isLog, setIsLog ] = useState(true)

  const isValid = username && username.length >= 3 && username.length <= 30
  const validUsername = isValid ? username : ''
  const logMessage = username && !isValid ? 'Incorrect username' : ''

  return (
     <MainWindow
      log={isLog ? logMessage  : ''}
     onClose={() => setIsLog(false)}
     >
       {validUsername ? <Login_password/> : <Login_login/>}
    </MainWindow>
  )
}