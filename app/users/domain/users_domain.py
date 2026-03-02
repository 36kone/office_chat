class UserDomain:

    @staticmethod
    def validate_email(email: str):
        if "@" not in email:
            raise ValueError("Email inválido")

        if not email.endswith("@empresa.com"):
            raise ValueError("Email deve ser corporativo")
    
    @staticmethod
    def validate_age(age: int):
        if age < 18:
            raise ValueError("Usuário precisa ser maior de idade")