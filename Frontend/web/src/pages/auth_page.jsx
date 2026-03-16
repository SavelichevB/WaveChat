import React, { use, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import {MainWindow, Reg_login, Reg_password, Login_login, Login_password} from '../components/auth/auth'
import { useParams } from 'react-router-dom'

export function RegistePage() {
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
       {validUsername ? <Reg_password/> : <Reg_login/>}
    </MainWindow>
  )
}

export function LoginPage() {
  const { username } = useParams()
  const { logs, setlogs } = useParams()
  const [ isLog, setIsLog ] = useState(true)

  const isValid = username && username.length >= 3 && username.length <= 60
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