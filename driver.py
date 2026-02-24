import git_parser

if __name__== "__main__":
    pushes = git_parser.get_commit_from_name("torvalds", 5)

    for p in pushes:
        print(p)

