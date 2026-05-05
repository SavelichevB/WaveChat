import { useState, useEffect } from "react"
import { api_users } from "../utils/user"
import { useAuth } from "./useAuth"

export function useUsers() {

    const [ id, setId ] = useState(null)
    const [ load, setLoad ] = useState(true)

    const { id: authId, load: authLoad } = useAuth() || {}

    const get_user_me = async () => {
        setLoad(true)
        try {
          const res = await api_users.get_user_me()
          if(res?.Success) {            
              return { Success: true, status: res._status, data: res.Data }
           }
           return { Success: false, status: res._status }
        }
        catch(error) {
            console.log('Error get personal data', error)
            return false
        }
        finally {
            setLoad(false)
        }
    }

    const get_user_id = async (id) => {
        setLoad(true)
        try {
            const res = await api_users.get_user_id(id)
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status }
        }
        catch(error) {
            console.log('Error get user data', error)
            return false           
        }
        finally {
            setLoad(false)
        }
    }

    const get_username_id = async (username) => {
        setLoad(true)
        try {
            const res = await api_users.get_username_id(username)
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status }
        }
        catch(error) {
            console.log('Error get user id', error)
            return false           
        }
        finally {
            setLoad(false)
        }
    }

    return {
        id, 
        load,
        get_username_id,
        get_user_id,
        get_user_me
    }
}