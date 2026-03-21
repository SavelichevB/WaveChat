
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
      return await res.json()
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
      return await res.json()
    }
    catch(error){
      return {
        Success: false
      }
    }
  }
}