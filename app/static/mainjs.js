 const section=document.querySelector("#sect-main")
        const options_menu = ["PIX","B","C","D","E","F","G","H"]
        const icons_menu = ["/static/img/Logo_do_Pix_em_Teal-removebg-preview.ico","icon-b","icon-c","icon-d","icon-e","icon-f","icon-g","icon-h"]
        const link_menu = ["","b","c","d","e","f","g","h"]
        let number=8

        for (let i=0;i<number;i++){
            const div=document.createElement("div")
            const h3=document.createElement("h3")
            h3.innerHTML=`${options_menu[i]}`
            div.className="box-body"
            div.appendChild(h3)
            link = document.createElement("a")
            link.href=`/pix`
            const img=document.createElement("img")
            img.src=`${icons_menu[i]}`
            img.className="icon-menu"
            link.appendChild(img)
            div.appendChild(link)
            section.appendChild(div)
        }
        console.log(section)
        
