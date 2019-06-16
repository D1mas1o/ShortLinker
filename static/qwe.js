function Complete2()
        {

            var login = document.getElementById("Login");
            var pass = document.getElementById("Password");



            if (login.length==0||login.length<5) {
                alert("Введите Логин (больше 5 символов)")
                return;
              }
            if (pass.length==0||pass.length<5) {
                alert("Введите Пароль (больше 5 символов)")
                return;
              }
            var myData =

            {
                Login: ""+document.Data.Login.value,
                Password: ""+document.Data.Password.value,
            };
            fetch('http://127.0.0.1:5000/login', {
              method: 'post',
            headers: {
             'Accept': 'application/json, text/plain, */*',
             'Content-Type': 'application/json'
             },
                body: JSON.stringify(myData)
                })

              }
location.

var links = {{links}}
                for (i=0,i<links.length,i++)
                {
                document.write('<td>')
                links[i][0]
                links[i][1]
                document.write('</td>')
                }
