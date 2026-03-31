
const API_URL = 'http://localhost:3333/'

const headers = {
  'Content-Type': 'application/json',
}

export const apiSend = {
  post: async (url, data) => {
    try{
      const res = await fetch(`${API_URL}${url}`, {
        method: 'POST',
        credentials: 'include',
        mode: 'cors',
        headers: headers,
        body: JSON.stringify(data)
      })
      const dataRes = await res.json()

      return {
        ...dataRes,
        _status: res.status
      }
    }
    catch(error){
      return {
        Success: false
      }
    }
  },

  get: async (url) => {
    try{
      const res = await fetch(`${API_URL}${url}`, {
        method: 'GET',
        credentials: 'include',
        mode: 'cors',
        headers: headers,
      })
      const dataRes = await res.json()

      return {
        ...dataRes,
        _status: res.status
      }
    }
    catch(error){
      return {
        Success: false
      }
    }
  }
}