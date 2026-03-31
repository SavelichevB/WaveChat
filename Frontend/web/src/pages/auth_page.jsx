import React, { use, useState } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import {MainWindow, Reg_login, Reg_password, Login_login, Login_password} from '../components/auth/auth'

export function RegistePage() {
  const { username } = useParams()
  const [ isLog, setIsLog ] = useState(true)
  const [ childLog, setChildLog] = useState('')


  const isValid = username && username.length >= 3 && username.length <= 30
  const validUsername = isValid ? username : ''
  const logMessage = username && !isValid ? 'Incorrect username' : ''

  const handleChild = (message) => {
    setChildLog(message)
  }
  const handleClose = () => {
    setIsLog(false),
    setChildLog('')
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
  const [ isLog, setIsLog ] = useState(true)
  const [ childLog, setChildLog] = useState('')

  const isValid = username && username.length >= 3 && username.length <= 30
  const validUsername = isValid ? username : ''
  const logMessage = username && !isValid ? 'Incorrect username' : ''

  const handleChild = (message) => {
    setChildLog(message)
  }
  const handleClose = () => {
    setIsLog(false),
    setChildLog('')
  }

  const displayLog = childLog || (isLog ? logMessage : '')

  return (
     <MainWindow
      log={displayLog}
     onClose={handleClose}
     >
       {validUsername ? <Login_password onLog={handleChild}/> : <Login_login/>}
    </MainWindow>
  )
}