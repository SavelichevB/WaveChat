import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { api_auth } from "../utils/auth"

export function useAuth() {
    const [id, setId] = useState(null)
    const [load, setLoad] = useState(true)
    const nav = useNavigate()

    useEffect(() => {
      const checkAuth = async () => {
         const res = await api_auth.check()
         if(res?.Success){
             setId(res.Client_id)
             nav('/k/')
         }
         setLoad(false)
      }

      checkAuth()
    }, [])

    const logout = async () => {
        setLoad(true)
        try{
            const res = await api_auth.logout()
            if(res?.Success){
                setId(null)
                nav('/')
                return true
            }
        }
        catch(error){
            console.log('Error logout: ', error)
            return false
        }
    }

    const login = async (username, password) => {
        setLoad(true)
        try{
           const res = await api_auth.login(username, password)
           if(res?.Success) {
             nav('/k/')
             return true
           }
           else {
             return false
           }
        }
        catch(error){
            console.log('Login error: ', error)
            return false
        }
        finally {
            setLoad(false)
        }
    }

    const register = async (username, password) => {
        setLoad(true)
        try{
           const res = await api_auth.register(username, password)
           if(res?.Success) {
             nav('/k/')
             return true
           }
           else {
             return false
           }
        }
        catch(error){
            console.log('Register error: ', error)
            return false
        }
        finally {
            setLoad(false)
        }
    }

    return {
       isAuth: !!id,
       id,
       load,
       logout,
       login, 
       register
    }
}