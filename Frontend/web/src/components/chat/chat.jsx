import React, { use, useCallback, useEffect, useState } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import { useBodyClass } from '../../hooks/useBody'
import { useUsers } from '../../hooks/useUsers'
import { useChat } from '../../hooks/useChat'
import { useMessage } from '../../hooks/useMessage' 
import { useSocket } from '../../hooks/useSocket'
import { formatTime, firstNameChat, formatTimeHour, formatTimeChat } from '../../utils/route_config'
import './chat.css'
import '../index.css'

export function Main_chats({ initUsername }) {
  
  useBodyClass('chat-bg')
  const [ selectedChat, setSelectedChat ] = useState(null)
  const [ selectUserChat, setUserChat ] = useState(null)
  const { id: userId, get_chat_username } = useChat()
  const { get_chat } = useChat()
  const [ chatListData, setChatListData ] = useState(null)
  const nav = useNavigate()

  useEffect(() => {
    const getChatId = async () => {
        if(!initUsername) return

        const res = await get_chat_username(initUsername)
        if(res.Success && res.data) {
          if(res.data.chat_id){
            setSelectedChat(res.data.chat_id)
            setUserChat(null)
          }
          else {
            setUserChat(res.data.client_id)
            setSelectedChat(null)
          }
        } else {
           nav('/k/')
        }
    }
    getChatId()
  }, [initUsername])

  const updateChats = useCallback(async () => {
      const res = await get_chat()
      if(res.Success) {
         setChatListData(res.data)
      }
  }, [get_chat, setChatListData])

  return (
   <div className='controls'>
    <div className='main'>
        <div className='list-chats'>
            <List_chats 
              chatListData={chatListData}
              setChatListData={setChatListData}
              selectedChat={selectedChat}
              onSelectedChat={setSelectedChat}
              userId={userId}
            />
        </div>
        <div className='message-chats'>
            <Message_chats
             updateChats={updateChats}
             selectedChat={selectedChat}
             onSelectedChat={setSelectedChat}
             selectUserChat={selectUserChat}
             userId={userId}
             />
        </div>
    </div>
   </div>
  )
}

export function List_chats({ chatListData, setChatListData, selectedChat, onSelectedChat, userId }) {
    const { load, get_user_me } = useUsers()
    const [ userData, setUserData ] = useState(null)
    const { ChatLoad=load, get_chat } = useChat()
    const nav = useNavigate()

    useEffect(() => {
        const fetchUser = async () => {
            const res = await get_user_me()
            if(res.Success) {
                setUserData(res.data)
            }
        }
        const fetchChats = async () => {
            const res = await get_chat()
            if(res.Success) {
                setChatListData(res.data)
            }
        }
        fetchUser()
        fetchChats()
    }, [])

    const handleSelectChat = (chat) => {
        if(chat.chat_id) {
            onSelectedChat(chat.chat_id)
            if(chat.username) {
                nav(`/k/@${chat.username || ''}`)
            }
        }
        else {
            nav('/k/')
        }
    }

    return (
        <>
         <div className='list-block'>
             <div className='search-user'>
                    <input type='text' placeholder='Поиск'/>
                    <i className="fa-solid fa-magnifying-glass"></i>
             </div>
             <div className='active-chats'>
                 { ChatLoad ? (
                  <>
                    <div className='chat' style={{pointerEvents: 'none'}}><div className='load-section'></div></div>
                    <div className='chat' style={{pointerEvents: 'none'}}><div className='load-section'></div></div>
                    <div className='chat' style={{pointerEvents: 'none'}}><div className='load-section'></div></div>
                    <div className='chat' style={{pointerEvents: 'none'}}><div className='load-section'></div></div>
                  </>
                 ) : chatListData && chatListData.length > 0 ? (
                    chatListData.map((chat) => ( 
                        <div
                            key={chat.chat_id}
                            className={`chat ${Number(selectedChat) === Number(chat.chat_id) ? 'active' : ''}`}
                            onClick={() => handleSelectChat(chat)}
                        >
                          <div className='chat-info-block'>
                             <div className='user-img'>{firstNameChat(chat.name)}</div>
                             <div className='chat-info'>
                               <div className='chat-name'>{chat.name}</div>
                               <div className='end-message'>
                                 { userData?.id === chat?.last_sender_id ? (
                                  chat.last_message ?
                                  (
                                    <>
                                       <b>Вы:</b> {chat.last_message}
                                    </>
                                  )
                                  :
                                  <>Пока пусто</>
                                ) : 
                                    chat.last_message ? (
                                        <>
                                          <b>{chat.name}:</b> {chat.last_message}
                                        </>
                                    )
                                    : 'Нету сообщений'
                                }
                                </div>
                            </div>
                            <div className='config-chat-info'>
                              <div className='last-message-time'>
                                  {
                                      chat.last_message_time && formatTime(chat.last_message_time)
                                  }
                              </div>
                              { chat.unread > 0 &&
                               (
                                  <>
                                    <div className='notification-message'>
                                        { chat.unread > 999 ? '999+' : chat.unread }
                                    </div>
                                  </>
                               ) 
                              }                             
                            </div>
                         </div>                            
                       </div>
                    ))
                 ) : (
                    <div className='none-chat'>Пока пусто...</div>
                 )}
             </div>

             <div className='user-info'>
                 { load ? <div className='load-section'></div> : 
                  (   
                    <>
                     <div className='user-avatar'>{  userData?.username?.[0] || '?' }</div>
                     <div className='user-text'>
                         <div className='user-name'>{ userData?.name || 'Аноним' }</div>
                       <div className='user-tag'>@{ userData?.username || '?' }</div>
                     </div>
                     <a><i className="fa-solid fa-plus"></i></a>
                    </>           
                  )}
             </div>
         </div>
        </>
    )
}

export function Message_chats({ updateChats, selectedChat, onSelectedChat, selectUserChat, userId }) {

    const { get_chat_info } = useChat()
    const { get_user_id } = useUsers()
    const { load: loadSend, send_message_chat_id, send_message_user_id } = useMessage()
    const { sendMessage, onMessage, onLog, onError, readMessage } = useSocket(userId)
    const [ chatData, setChatData ] = useState(null)
    const [ userData, setUserData ] = useState(null)
    const [ isLoad, setIsLoad ] = useState(false)
    const [ clientText, setClientText ] = useState('')
    const [ messagesData, setMessagesData ] = useState(null)

    useEffect(() => {
        setChatData(null)
        setUserData(null)

        const fetchChatsInfo = async () => {
            setIsLoad(true)
            const res = await get_chat_info(selectedChat)
            if(res.Success) {
                setChatData(res.data)
            }
            setIsLoad(false)
        }
        const fetchUserInfo = async () => {
            setIsLoad(true)
            const res = await get_user_id(selectUserChat)
            if(res.Success) {
                setUserData(res.data)
            }
            setIsLoad(false)
        }

        if(selectedChat) {
          fetchChatsInfo()
        }
        if(selectUserChat) {
          fetchUserInfo() 
        }

    }, [selectedChat, selectUserChat])

    useEffect(() => {
        if(chatData?.chat_id && selectedChat) {
            handleReadMessage()
        }
    }, [chatData, selectedChat])

  const scrollToBottom = () => {
    setTimeout(() => {
        const container = document.querySelector('.all-message')
        if (container) {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
        }
    }, 50)
  }

  const handleSendMessage = async () => {
    if(!clientText?.trim()) return

    const tempId = Date.now()
    const text = clientText

    setMessagesData(prev => [...(prev || []), {
        id: tempId,
        from_id: userId,
        text: text,
        time: new Date().toISOString(),
        is_temp: true
    }])
    setClientText('')
    scrollToBottom()


    if(chatData?.chat_id) {
        sendMessage(chatData.chat_id, null, text, tempId)
    } else if(selectUserChat || userData?.id) {
        const toId = selectUserChat || userData?.id
        sendMessage(null, toId, text, tempId)
    }
    updateChats()
  }

  const handleReadMessage = async () => {
     if(messagesData) {
        if(chatData?.chat_id) {
            readMessage(chatData?.chat_id)
        }
     }
  }

  useEffect(() => {
     const unsub = onLog((data) => {
        if(data.success && data.temp_id) {
            setMessagesData(prev => prev.map(msg =>
                msg.id === data.temp_id ? { ...msg, is_temp: false, id: data.message_id } : msg
            ))
        }
     })
     return () => unsub?.()
  }, [onLog])


    if(isLoad) { 
        return (
        <div className='message-block'>
            <div className='tab-block'>
                <div className='tab-avatar' style={{background: 'transparent'}}><div className='load-section'></div></div>
                <div className='tab-info'>
                       <div className='load-section' style={{width: '100%', height: '30px'}}></div>
                </div>
                <div className='bars-tab'>
                      <i className="fa-solid fa-bars"></i>
                </div>
            </div>
            <div className='all-message'>
                 <Get_message />               
            </div>
            <div className='input-block'>
                <div className='input-message'>
                   <a><div className="load-mini"></div></a>
                   <textarea
                    placeholder='Загрузка...'
                    disabled={true}
                   ></textarea>
                </div>
                <a className='send-message' style={{opacity: '90%'}}><div className="load-mini"></div></a>
            </div>
        </div>           
        )
    }

    if(chatData) {
        return (
        <div className='message-block'>
            <div className='tab-block'>
                   <div className='tab-avatar'>{firstNameChat(chatData?.name)}</div>
                   <div className='tab-info'>
                       <div className='tab-name'>{chatData?.name || 'Неизвестно'}</div>
                       <div className='tab-status'>Был(а) недавно</div>
                   </div>
                   <div className='bars-tab'>
                      <i className="fa-solid fa-bars"></i>
                   </div>
            </div>
            <div className='all-message'>
                 <Get_message
                   updateChats={updateChats}
                   chatData={chatData}
                   userData={null}
                   userId={userId}
                   onSelectedChat={onSelectedChat}
                   messagesData={messagesData}
                   setMessagesData={setMessagesData}
                   handleReadMessage={handleReadMessage}
                  />               
            </div>
            <div className='input-block'>
                <div className='input-message'>
                   <a onClick={() => alert('Скоро')}><i className="fa-solid fa-plus"></i></a>
                   <textarea 
                       placeholder='Сообщение'
                       value={clientText}
                       onChange={(e) => {
                         setClientText(e.target.value)
                       }}
                   ></textarea>
                </div>
                <a className='send-message'
                   onClick={() => handleSendMessage()}
                >
                  {loadSend ?
                   <div className="load-mini"></div> : 
                   <i className="fa-solid fa-paper-plane"></i>
                  }
                </a>
            </div>
        </div>           
        )
    }

    if(userData) {
        return (
        <div className='message-block'>
            <div className='tab-block'>
                   <div className='tab-avatar'>{firstNameChat(userData?.name || userData?.username || '?')}</div>
                   <div className='tab-info'>
                       <div className='tab-name'>{userData?.name || userData?.username || 'Неизвестно'}</div>
                       <div className='tab-status'>Был(а) недавно</div>
                   </div>
                   <div className='bars-tab'>
                      <i className="fa-solid fa-bars"></i>
                   </div>
            </div>
            <div className='all-message'>
                 <Get_message
                   updateChats={updateChats}
                   chatData={null}
                   userData={userData}
                   userId={userId}
                   onSelectedChat={onSelectedChat}
                   messagesData={messagesData}
                   setMessagesData={setMessagesData}
                   handleReadMessage={handleReadMessage}
                  />               
            </div>
            <div className='input-block'>
                <div className='input-message'>
                   <a onClick={() => alert('Скоро')}><i className="fa-solid fa-plus"></i></a>
                   <textarea 
                       placeholder='Сообщение'
                       value={clientText}
                       onChange={(e) => {
                         setClientText(e.target.value)
                    }}
                       
                   ></textarea>
                </div>
                <a 
                className='send-message'
                onClick={() => handleSendMessage()}
                >
                  {loadSend ?
                   <div className="load-mini"></div> : 
                   <i className="fa-solid fa-paper-plane"></i>
                  }
                </a>
            </div>
        </div>
        )        
    }

    return (
        <div className='message-select-block'>
            <i className="fa-solid fa-bolt"></i>
            <h3>WaveChat</h3>
            <p>Быстро, безопасно</p>
        </div>
    )

}

export function Get_message({ updateChats, chatData, userData, userId, onSelectedChat, messagesData, setMessagesData, handleReadMessage }) {

    const { load, get_message } = useMessage()
    const { isConnected, sendMessage, onMessage, onLog, onError,
            delMessage, onDelMessage, onDelLog, onDelError,
            readMessage, onReadMessage } = useSocket(userId)

    const [ idBurgerMessage, setIdBurgerMessage ] = useState(null)

    const [ delMsgId, setDelMsgId ] = useState(null)

    useEffect(() => {
        const getMessages = async () => {
            if(!chatData?.chat_id) return

            const res = await get_message(chatData.chat_id)
            if(res.Success && res.data) {
                setMessagesData(res.data)
            }
            else {
                setMessagesData(null)
            }
            
            handleReadMessage()

        }
        if(chatData) {
            getMessages()
        }
    }, [chatData])

    useEffect(() => {
        const unsub = onMessage((msg) => {
        console.log('New message:', msg)
        updateChats()

            const isCurrentChat = 
              (chatData?.chat_id && msg.chat_id === chatData?.chat_id) ||
              (!chatData && userData?.id && msg.from_id === userData?.id)

            if(isCurrentChat) {
                setMessagesData(prev => [...(prev || []), {
                    id: msg.id,
                    from_id: msg.from_id,
                    text: msg.text,
                    time: msg.time,
                    is_temp: false
                }])
                 handleReadMessage()
            }
        })
        return () => unsub?.()
    }, [onMessage, handleReadMessage, chatData?.chat_id, userData?.id])

    useEffect(() => {
        const unsub = onDelMessage?.((data) => {
            const { message_id, chat_id } = data 
            try {
                setDelMsgId(message_id)
                setTimeout(() => {
                  setMessagesData(prev => prev.filter(msg => msg.id !== message_id))
                  updateChats()
                }, 300)
                if(idBurgerMessage === message_id) {
                    setIdBurgerMessage(null)
                }
                setTimeout(() => {
                   setDelMsgId(null)
                }, 600)
            }
            catch {
                return
            }
        })
        return () => unsub?.()
    },  [onDelMessage, chatData?.chat_id, userData?.id])

    useEffect(() => {
        const unsub = onDelLog?.((data) => {
            const { success, message_id }= data
            if(success) {
                if(idBurgerMessage === message_id) {
                    setIdBurgerMessage(null)
                }    
                setDelMsgId(message_id)
                setTimeout(() => {
                  setMessagesData(prev => prev.filter(msg => msg.id !== message_id))
                  updateChats()
                }, 300)
                setTimeout(() => {
                  setDelMsgId(null)
                }, 600)            
            }
        })
        return () => unsub?.()
    }, [onDelLog])

    useEffect(() => {
        const unsub = onReadMessage?.((data) => {
            console.log('Read your messages!')
            const { chat_id, count } = data

            if(chatData && chatData.chat_id == chat_id) {
                setMessagesData(prev => prev.map(msg => 
                    msg.from_id === userId ? { ...msg, is_read: 1 } : msg
                ))
            }
            updateChats()
        })
        return () => unsub?.()
    }, [onReadMessage, updateChats, userId])

    useEffect(() => {
        const closeMenu = (e) => {
           if (idBurgerMessage) {
               const isMenu = e.target.closest('.burger-message')
               const isMessage = e.target.closest('.message-bubble')
            
               if (!isMenu && !isMessage) {
                setIdBurgerMessage(null)
               }
            }
        }
        document.addEventListener('click', closeMenu)
        return () => document.removeEventListener('click', closeMenu)
    }, [idBurgerMessage])

    useEffect(() => {
        const container = document.querySelector('.all-message')
        if (container) {
          container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
        }
    }, [messagesData])

    const handleBurgerMessage = async (message_id) => {
       if(!message_id) return
       setIdBurgerMessage(idBurgerMessage === message_id ? null : message_id)
    } 
    const handleDelMessage = async (message_id) => {
      if(!message_id) return
      delMessage(message_id)
    }  
    
    if(load) {
       return (
         <LoadingMessage />     
       )
    }

    if(chatData && messagesData) {
        return (
        <>
           {messagesData.map((msg, index) => {
              const prevMsg = messagesData[index - 1]
              
              const currentDate = new Date(msg.time).toISOString().split('T')[0]
              const prevDate = prevMsg ? new Date(prevMsg.time).toISOString().split('T')[0] : null
              const showDate = index === 0 || currentDate !== prevDate

              
              return (
                <React.Fragment key={msg.id}>
                {showDate && (
                  <div className='message-info'>
                      {formatTimeChat(msg.time)}
                  </div>                      
                )}
                <div className={Number(msg.from_id) === Number(userId) ? 'message-own' : 'message-other'}>
                     {(idBurgerMessage === msg.id) && (
                      <>
                        
                        <div className='burger-message'>
                          <label>
                              <i className="fa-solid fa-copy"></i>
                              <section>Скопировать</section>
                          </label>
                           { Number(userId) === Number(msg.from_id) && (
                               <label onClick={() => handleDelMessage(msg.id)}>
                                  <i className="fa-solid fa-trash"></i>
                                  <section>Удалить</section>
                               </label>
                           )}
                        </div>   
                      </>                     
                     )}
                     <div
                      className={`message-bubble ${delMsgId === msg.id ? 'del' : ''}`}
                       onClick={() => handleBurgerMessage(msg.id)}
                      >
                         <div className='message-text'>{msg.text}</div>
                         <div className='message-time'>
                           {formatTimeHour(msg.time)} 
                           { msg?.is_temp && ( <i className="fa-regular fa-hourglass"></i> ) }
                           { Number(msg.from_id) === Number(userId) && msg.is_read == 0 && ( <i className="fa-solid fa-check"></i> )  }
                           { Number(msg.from_id) === Number(userId) && msg.is_read == 1 && ( <i className="fa-solid fa-check-double"></i> ) }
                         </div>
                     </div>
                </div> 
                </React.Fragment>
              )
           })} 
        </>            
        )
    }

    if(userData) {
        if(Number(userId) === Number(userData.id)) {
           return (
              <div className='message-info'>
                   Вы не можете написать самому себе :(
              </div>               
           )
        }
        if(messagesData && messagesData.length > 0) {
            return (
              <>
                {messagesData.map((msg, index) => {
                    const prevMsg = messagesData[index - 1]   

                   const currentDate = new Date(msg.time).toISOString().split('T')[0]
                   const prevDate = prevMsg ? new Date(prevMsg.time).toISOString().split('T')[0] : null
                   const showDate = index === 0 || currentDate !== prevDate

              return (
                <React.Fragment key={msg.id}>
                {showDate && (
                  <div className='message-info'>
                      {formatTimeChat(msg.time)}
                  </div>                      
                )}
                <div className={Number(msg.from_id) === Number(userId) ? 'message-own' : 'message-other'}>
                     <div className='message-bubble'>
                         <div className='message-text'>{msg.text}</div>
                         <div className='message-time'>
                           {formatTimeHour(msg.time)} 
                           { msg?.is_temp && ( <i className="fa-regular fa-hourglass"></i> ) }
                           { !msg?.is_temp && Number(msg.from_id) === Number(userId) <= 0 && ( <i className="fa-solid fa-check"></i> )  }
                         </div>
                     </div>
                </div> 
                </React.Fragment>
              )
              })}
              </>
            )
       }    
       else {
          return (
              <div className='message-info'>
                  Напишите сообщение, чтобы начать общение
              </div>
           )
       }
    }

       return (
        <> 
              <div className='message-info'>
                  Напишите сообщение, чтобы начать общение
              </div>
        </>       
       )
}

export function LoadingMessage() {
       return (
        <div className='loading-messages'>
            <div className='message-other'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                    <div className='message-text'><div style={{width: '110px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div>
            <div className='message-info'>
                  <div style={{width: '80px', height: '20px'}} className='load-section'></div>
            </div>  
            <div className='message-own'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                     <div className='message-text'><div style={{width: '130px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div>    
            <div className='message-own'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                     <div className='message-text'><div style={{width: '120px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div>  
            <div className='message-other'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                    <div className='message-text'><div style={{width: '100px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div>
            <div className='message-other'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                    <div className='message-text'><div style={{width: '160px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div>
            <div className='message-own'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                     <div className='message-text'><div style={{width: '100px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div> 
            <div className='message-info'>
                  <div style={{width: '80px', height: '20px'}} className='load-section'></div>
            </div>  
            <div className='message-other'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                    <div className='message-text'><div style={{width: '120px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div> 
            <div className='message-info'>
                  <div style={{width: '80px', height: '20px'}} className='load-section'></div>
            </div>  
            <div className='message-other'>
                <div className='message-bubble' style={{ padding: '2px'}}>
                    <div className='message-text'><div style={{width: '120px', height: '43px'}} className='load-section'></div></div>     
                </div>
            </div> 
        </div>       
    )    
}